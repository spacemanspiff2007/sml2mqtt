import logging
import sml2mqtt
import traceback
from asyncio import Future, create_task

from asyncio_mqtt import Client, MqttError, Will

from .config import CONFIG

log = logging.getLogger('sml.mqtt')

MQTT: Client = None
CONNECT: Future = None


async def _connect():
    global MQTT, CONNECT

    wait = 1

    while True:
        try:
            will_topic = CONFIG.mqtt.topics.get_topic(CONFIG.mqtt.topics.last_will)

            MQTT = Client(
                hostname=CONFIG.mqtt.connection.host,
                port=CONFIG.mqtt.connection.port,
                username=CONFIG.mqtt.connection.user if CONFIG.mqtt.connection.user else None,
                password=CONFIG.mqtt.connection.password if CONFIG.mqtt.connection.password else None,
                will=Will(will_topic, payload='OFFLINE')
            )

            # We don't publish anything if we just analyze the data from the reader
            if sml2mqtt._args.ARGS.analyze:
                return None

            await MQTT.connect()

            # signal that we are online
            await publish(will_topic, 'ONLINE')
            wait = 1
            break

        except MqttError as e:
            log.error(e)
            wait = min(180, wait * 2)
        except Exception:
            for line in traceback.format_exc().splitlines():
                log.error(line)
            return None

    CONNECT = None


async def connect():
    global CONNECT
    if CONNECT is None:
        CONNECT = create_task(_connect())


async def publish(topic, value):
    global CONNECT

    if not MQTT._client.is_connected():
        # try to connect
        if CONNECT is None:
            CONNECT = create_task(_connect())
        return None

    # publish message
    try:
        await MQTT.publish(topic, value, qos=CONFIG.mqtt.publish.qos, retain=CONFIG.mqtt.publish.retain)
    except MqttError as e:
        log.error(e)
