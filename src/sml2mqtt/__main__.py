import asyncio
import platform
import sys
import traceback
import typing

from sml2mqtt import mqtt
from sml2mqtt.__args__ import CMD_ARGS, get_command_line_args
from sml2mqtt.__log__ import log, setup_log
from sml2mqtt.__shutdown__ import get_return_code, shutdown, signal_handler_setup
from sml2mqtt.config import CONFIG
from sml2mqtt.config.source import SerialSourceSettings, HttpSourceSettings
from sml2mqtt.sml_device import SmlDevice
from sml2mqtt.const.task import wait_for_tasks
from sml2mqtt.sml_source import create_source


async def a_main():
    devices = []

    try:
        if CMD_ARGS.analyze:
            mqtt.patch_analyze()
        else:
            # initial mqtt connect
            mqtt.start()
            await mqtt.wait_for_connect(5)

        # Create devices for port
        for input_cfg in CONFIG.inputs:
            device = SmlDevice(input_cfg.get_device_name())
            device.set_source(await create_source(device, settings=input_cfg))
            devices.append(device)

        for device in devices:
            await device.start()

    except Exception as e:
        shutdown(e)

    return await asyncio.gather(wait_for_tasks(), mqtt.wait_for_disconnect())


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
        mqtt.setup_base_topic(CONFIG.mqtt.topic, CONFIG.mqtt.defaults.qos, CONFIG.mqtt.defaults.retain)

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
