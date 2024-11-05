import traceback
from asyncio import CancelledError, Event, Queue, TimeoutError, wait_for
from typing import Final

from aiomqtt import Client, MqttError, Will

import sml2mqtt
from sml2mqtt.__log__ import log as _parent_logger
from sml2mqtt.const import Task
from sml2mqtt.errors import InitialMqttConnectionFailedError
from sml2mqtt.mqtt import DynDelay
from sml2mqtt.runtime import on_shutdown


log = _parent_logger.getChild('mqtt')


TASK: Task | None = None
IS_CONNECTED: Event | None = None


async def start() -> None:
    global IS_CONNECTED, TASK

    assert TASK is None

    IS_CONNECTED = Event()
    TASK = Task(_mqtt_task, name='MQTT Task')

    on_shutdown(TASK.cancel_and_wait, 'Shutdown mqtt')
    TASK.start()


async def wait_for_connect(timeout: float):
    if IS_CONNECTED is None:
        raise ValueError()

    try:
        await wait_for(IS_CONNECTED.wait(), timeout)
    except TimeoutError:
        log.error('Initial mqtt connection failed!')
        raise InitialMqttConnectionFailedError() from None

    return None


QUEUE: Queue[tuple[str, int | float | str | bytes, int, bool]] | None = None


async def _mqtt_task() -> None:
    global QUEUE

    from .mqtt_obj import BASE_TOPIC
    config = sml2mqtt.config.CONFIG

    cfg_connection = config.mqtt.connection

    delay = DynDelay(0, 300)

    payload_online: Final = 'ONLINE'
    payload_offline: Final = 'OFFLINE'

    shutdown = False

    while not shutdown:
        await delay.wait()

        try:
            # since we just pass this into the mqtt wrapper we do not link it to the base topic
            will_topic = BASE_TOPIC.create_child(topic_fragment='status').set_config(config.mqtt.last_will)

            will = Will(
                topic=will_topic.topic, payload=payload_offline,
                qos=will_topic.qos, retain=will_topic.retain
            )

            tls_kwargs = {} if cfg_connection.tls is None else cfg_connection.tls.get_client_kwargs(log)

            client = Client(
                hostname=cfg_connection.host, port=cfg_connection.port,

                username=cfg_connection.user if cfg_connection.user else None,
                password=cfg_connection.password if cfg_connection.password else None,
                will=will,
                identifier=cfg_connection.identifier,

                **tls_kwargs
            )

            log.debug(f'Connecting to {cfg_connection.host}:{cfg_connection.port}')

            async with client:
                log.debug('Success!')
                delay.reset()
                QUEUE = Queue()
                IS_CONNECTED.set()

                try:
                    # signal that we are online
                    await client.publish(will.topic, payload_online, will.qos, will.retain)

                    # worker to publish things
                    while True:
                        topic, value, qos, retain = await QUEUE.get()
                        await client.publish(topic, value, qos, retain)
                        QUEUE.task_done()

                except CancelledError:
                    # The last will testament only gets sent on abnormal disconnect
                    # Since we disconnect gracefully we have to manually sent the offline status
                    await client.publish(will.topic, will.payload, will.qos, will.retain)
                    shutdown = True
                    log.debug('Disconnecting')

        except MqttError as e:
            delay.increase()
            log.error(f'{e} ({e.__class__.__name__})')

        except Exception:
            delay.increase()
            for line in traceback.format_exc().splitlines():
                log.error(line)

        finally:
            QUEUE = None
            IS_CONNECTED.clear()


def publish(topic: str, value: int | float | str | bytes, qos: int, retain: bool) -> None:
    if QUEUE is not None:
        QUEUE.put_nowait((topic, value, qos, retain))
