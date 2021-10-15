import time
import traceback
from asyncio import create_task, Future
from typing import Optional, Union

from asyncio_mqtt import Client, MqttError, Will

import sml2mqtt
from sml2mqtt.__log__ import log as _parent_logger

# from sml2mqtt.config import CONFIG
from sml2mqtt.mqtt import DynDelay

log = _parent_logger.getChild('mqtt')

TIME_BEFORE_RECONNECT = 15
DELAY_CONNECT = DynDelay(0, 180)

MQTT: Optional[Client] = None
TASK_CONNECT: Optional[Future] = None


async def disconnect():
    global TASK_CONNECT, MQTT

    if TASK_CONNECT is not None:
        TASK_CONNECT.cancel()
        TASK_CONNECT = None

    if MQTT is not None:
        mqtt = MQTT
        MQTT = None
        if mqtt._client.is_connected():
            await mqtt.disconnect()


async def connect():
    global TASK_CONNECT
    if TASK_CONNECT is None:
        TASK_CONNECT = create_task(_connect_to_broker())


async def _connect_task():
    global TASK_CONNECT
    try:
        await _connect_to_broker()
    finally:
        TASK_CONNECT = None


async def _connect_to_broker():
    global MQTT

    # # We don't publish anything if we just analyze the data from the reader
    # if sml2mqtt._args.ARGS.analyze:
    #     return None

    config = sml2mqtt.config.CONFIG

    while True:
        try:
            async with DELAY_CONNECT:
                # If we are already connected we try to disconnect before we reconnect
                try:
                    if MQTT is not None:
                        if MQTT._client.is_connected():
                            await MQTT.disconnect()
                        MQTT = None
                except Exception as e:
                    log.error(f'Error while disconnecting: {e}')

                # since we just pass this into the mqtt wrapper we do not link it to the base topic
                will_topic = sml2mqtt.mqtt.MqttObj(
                    config.mqtt.base.topic, config.mqtt.base.qos, config.mqtt.base.retain
                ).update().create_child(config.mqtt.last_will)
                will_topic.set_config(config.mqtt.last_will)

                MQTT = Client(
                    hostname=config.mqtt.connection.host,
                    port=config.mqtt.connection.port,
                    username=config.mqtt.connection.user if config.mqtt.connection.user else None,
                    password=config.mqtt.connection.password if config.mqtt.connection.password else None,
                    will=Will(will_topic.topic, payload='OFFLINE', qos=will_topic.qos, retain=will_topic.retain)
                )

                log.debug(f'Connecting to {config.mqtt.connection.host}:{config.mqtt.connection.port}')
                await MQTT.connect()
                log.debug('Success!')

                # signal that we are online
                will_topic.publish('ONLINE')
                break

        except MqttError as e:
            log.error(f'{e} ({e.__class__.__name__})')
        except Exception:
            for line in traceback.format_exc().splitlines():
                log.error(line)
            return None


PUBS_FAILED_SINCE: Optional[float] = None


async def publish(topic: str, value: Union[int, float, str], qos: int, retain: bool):
    global PUBS_FAILED_SINCE

    if MQTT is None or not MQTT._client.is_connected():
        await connect()
        return None

    # publish message
    try:
        await MQTT.publish(topic, value, qos=qos, retain=retain)
        PUBS_FAILED_SINCE = None
    except MqttError as e:
        log.error(f'Error while publishing to {topic}: {e} ({e.__class__.__name__})')

        # If we fail too often we try to reconnect
        if PUBS_FAILED_SINCE is None:
            PUBS_FAILED_SINCE = time.time()
        else:
            if time.time() - PUBS_FAILED_SINCE >= TIME_BEFORE_RECONNECT:
                await connect()
