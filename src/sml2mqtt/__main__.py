import asyncio
import os
import sys
import traceback

from sml2mqtt import mqtt
from sml2mqtt.__args__ import CMD_ARGS, get_command_line_args
from sml2mqtt.__log__ import log, setup_log
from sml2mqtt.config import CONFIG, cleanup_validation_errors
from sml2mqtt.const.task import wait_for_tasks
from sml2mqtt.runtime import do_shutdown_async, on_shutdown, signal_handler_setup
from sml2mqtt.sml_device import ALL_DEVICES, SmlDevice
from sml2mqtt.sml_source import create_source


async def a_main() -> None:
    # Add possibility to stop program with Ctrl + c
    signal_handler_setup()

    on_shutdown(ALL_DEVICES.cancel_and_wait, 'Stop devices')

    try:
        if analyze := CMD_ARGS.analyze:
            mqtt.patch_analyze()
        else:
            # initial mqtt connect
            await mqtt.start()
            await mqtt.wait_for_connect(5)

        # Create device for each input
        for input_cfg in CONFIG.inputs:
            device = ALL_DEVICES.add_device(SmlDevice(input_cfg.get_device_name()))
            device.set_source(await create_source(device, settings=input_cfg))
            device.watchdog.set_timeout(input_cfg.timeout)
            if analyze:
                device.frame_handler = device.analyze_frame

        # Start all devices
        log.debug(f'Starting {len(ALL_DEVICES):d} device{"" if len(ALL_DEVICES) == 1 else "s":s}')
        await ALL_DEVICES.start()

    except Exception as e:
        log.error(f'{e.__class__.__name__} during startup: {e}')
        for line in traceback.format_exc().splitlines():
            log.error(line)

        await do_shutdown_async()

    # Keep tasks running
    await wait_for_tasks()


def main() -> int | str:
    # This is needed to make async-mqtt work
    # see https://github.com/sbtinstruments/asyncio-mqtt
    if sys.platform.lower() == 'win32' or os.name.lower() == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Load config
    try:
        CONFIG.load_config_file(get_command_line_args().config)
    except Exception as e:
        print(cleanup_validation_errors(str(e)))
        return 2

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

    return 0


if __name__ == '__main__':
    ret = main()
    log.info(f'Closed with return code {ret}')
    sys.exit(ret)
