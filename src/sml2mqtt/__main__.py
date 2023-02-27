import asyncio
import platform
import sys
import traceback
import typing

from sml2mqtt.__args__ import get_command_line_args
from sml2mqtt.__log__ import log, setup_log
from sml2mqtt.__shutdown__ import get_return_code, shutdown, signal_handler_setup
from sml2mqtt.config import CONFIG
from sml2mqtt.device import Device
from sml2mqtt.mqtt import BASE_TOPIC, connect


async def a_main():
    await connect()
    await asyncio.sleep(0.1)  # Wait till mqtt is connected

    # Create devices for port
    try:
        devices = []

        for port_cfg in CONFIG.ports:
            dev_mqtt = BASE_TOPIC.create_child(port_cfg.url)
            device = await Device.create(port_cfg, port_cfg.timeout, set(), dev_mqtt)
            devices.append(device)

        for device in devices:
            device.start()

    except Exception as e:
        shutdown(e)

    return await asyncio.gather(*devices)


def main() -> typing.Union[int, str]:
    try:
        CONFIG.load_config_file(get_command_line_args().config)
    except Exception as e:
        print(e)
        return 7

    # This is needed to make async-mqtt work
    # see https://github.com/sbtinstruments/asyncio-mqtt
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Add possibility to stop program with Ctrl + c
    signal_handler_setup()

    try:
        setup_log()

        # setup mqtt base topic
        BASE_TOPIC.cfg.topic_fragment = CONFIG.mqtt.topic
        BASE_TOPIC.cfg.qos = CONFIG.mqtt.defaults.qos
        BASE_TOPIC.cfg.retain = CONFIG.mqtt.defaults.retain
        BASE_TOPIC.update()

        asyncio.run(a_main())
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)

    return get_return_code()


if __name__ == "__main__":
    ret = main()
    log.info(f'Closed with return code {ret}')
    sys.exit(ret)
