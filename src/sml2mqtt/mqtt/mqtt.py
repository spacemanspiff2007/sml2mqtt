import traceback
from asyncio import CancelledError, create_task, Event, Queue, Task, TimeoutError, wait_for
from typing import Final, Optional, Union

from asyncio_mqtt import Client, MqttError, Will

import sml2mqtt
from sml2mqtt.__log__ import log as _parent_logger
from sml2mqtt.errors import InitialMqttConnectionFailedError
from sml2mqtt.mqtt import DynDelay

log = _parent_logger.getChild('mqtt')


TASK: Optional[Task] = None
IS_CONNECTED: Optional[Event] = None


def start():
    global TASK, IS_CONNECTED

    IS_CONNECTED = Event()

    assert TASK is None
    TASK = create_task(mqtt_task(), name='MQTT Task')


def cancel():
    global TASK
    if TASK is not None:
        TASK.cancel()
        TASK = None


async def wait_for_connect(timeout: float):
    if IS_CONNECTED is None:
        return None

    try:
        await wait_for(IS_CONNECTED.wait(), timeout)
    except TimeoutError:
        log.error('Initial mqtt connection failed!')
        raise InitialMqttConnectionFailedError() from None

    return None


async def wait_for_disconnect():
    if TASK is None:
        return None

    await TASK


QUEUE: Optional[Queue] = None


async def mqtt_task():
    try:
        await _mqtt_task()
    finally:
        log.debug('Task finished')


async def _mqtt_task():
    global QUEUE

    from .mqtt_obj import BASE_TOPIC
    config = sml2mqtt.config.CONFIG

    cfg_connection = config.mqtt.connection

    delay = DynDelay(0, 300)

    payload_offline: Final = 'OFFLINE'
    payload_online: Final = 'ONLINE'

    shutdown = False

    while not shutdown:
        await delay.wait()

        try:
            # since we just pass this into the mqtt wrapper we do not link it to the base topic
            will_topic = BASE_TOPIC.create_child(
                topic_fragment=config.mqtt.last_will.topic).set_config(config.mqtt.last_will)

            client = Client(
                hostname=cfg_connection.host,
                port=cfg_connection.port,
                username=cfg_connection.user if cfg_connection.user else None,
                password=cfg_connection.password if cfg_connection.password else None,
                will=Will(will_topic.topic, payload=payload_offline, qos=will_topic.qos, retain=will_topic.retain),
                client_id=cfg_connection.client_id
            )

            log.debug(f'Connecting to {cfg_connection.host}:{cfg_connection.port}')

            async with client:
                log.debug('Success!')
                delay.reset()
                QUEUE = Queue()
                IS_CONNECTED.set()

                try:
                    # signal that we are online
                    await client.publish(will_topic.topic, payload_online, will_topic.qos, will_topic.retain)

                    # worker to publish things
                    while True:
                        topic, value, qos, retain = await QUEUE.get()
                        await client.publish(topic, value, qos, retain)
                        QUEUE.task_done()
                except CancelledError:
                    # The last will testament only gets sent on abnormal disconnect
                    # Since we disconnect gracefully we have to manually sent the offline status
                    await client.publish(will_topic.topic, payload_offline, will_topic.qos, will_topic.retain)
                    shutdown = True

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


def publish(topic: str, value: Union[int, float, str], qos: int, retain: bool):
    if QUEUE is not None:
        QUEUE.put_nowait((topic, value, qos, retain))
