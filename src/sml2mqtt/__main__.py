import asyncio
import platform
import sys
import traceback
import typing

from sml2mqtt.__args__ import get_command_line_args
from sml2mqtt.__log__ import log, setup_log
from sml2mqtt.__shutdown__ import get_return_code, setup_signal_handler, shutdown
from sml2mqtt.config import CONFIG
from sml2mqtt.device import Device
from sml2mqtt.mqtt import BASE_TOPIC, connect


async def a_main():
    await connect()
    await asyncio.sleep(0.1)  # Wait till mqtt is connected

    # Create devices for port
    try:
        for port_cfg in CONFIG.ports:
            dev_mqtt = BASE_TOPIC.create_child(port_cfg.url)
            await Device.create(port_cfg.url, port_cfg.timeout, set(), dev_mqtt)

    except Exception as e:
        shutdown(e)


def main() -> typing.Union[int, str]:
    try:
        CONFIG.load_config_file(get_command_line_args().config)
    except Exception as e:
        print(e)
        return 7

    # This is needed to make async-mqtt work
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Add possibility to stop program with Ctrl + c
    setup_signal_handler()
    loop = None

    try:
        setup_log()

        # setup mqtt base topic
        BASE_TOPIC.cfg.topic_fragment = CONFIG.mqtt.topic
        BASE_TOPIC.cfg.qos = CONFIG.mqtt.defaults.qos
        BASE_TOPIC.cfg.retain = CONFIG.mqtt.defaults.retain
        BASE_TOPIC.update()

        # setup loop
        loop = asyncio.get_event_loop_policy().get_event_loop()
        loop.create_task(a_main())
        loop.run_forever()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        if loop is not None:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    return get_return_code()


if __name__ == "__main__":
    ret = main()
    log.info(f'Closed with return code {ret}')
    sys.exit(ret)
