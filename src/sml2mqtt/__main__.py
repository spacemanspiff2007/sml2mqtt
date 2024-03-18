import asyncio
import platform
import sys
import traceback

from sml2mqtt import mqtt
from sml2mqtt.__args__ import CMD_ARGS, get_command_line_args
from sml2mqtt.__log__ import log, setup_log
from sml2mqtt.config import CONFIG
from sml2mqtt.const.task import wait_for_tasks
from sml2mqtt.runtime import do_shutdown_async, signal_handler_setup, on_shutdown
from sml2mqtt.sml_device import ALL_DEVICES, SmlDevice
from sml2mqtt.sml_source import create_source


async def a_main():
    # Add possibility to stop program with Ctrl + c
    signal_handler_setup()

    on_shutdown(ALL_DEVICES.cancel_and_wait(), 'Stop devices')

    try:
        if CMD_ARGS.analyze:
            mqtt.patch_analyze()
        else:
            # initial mqtt connect
            await mqtt.start()
            await mqtt.wait_for_connect(5)

        # Create device for each input
        for input_cfg in CONFIG.inputs:
            device = ALL_DEVICES.add_device(SmlDevice(input_cfg.get_device_name()))
            device.set_source(await create_source(device, settings=input_cfg))

        # Start all devices
        await ALL_DEVICES.start()

    except Exception:
        await do_shutdown_async()

    # Shutdown everything
    try:
        await asyncio.wait_for(wait_for_tasks(), timeout=8.0)
    except TimeoutError:
        msg = 'Timeout while waiting for shutdown!'
        print(msg)
        log.error(msg)


def main() -> int | str:
    # This is needed to make async-mqtt work
    # see https://github.com/sbtinstruments/asyncio-mqtt
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Load config
    try:
        CONFIG.load_config_file(get_command_line_args().config)
    except Exception as e:
        print(e)
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

    return 1


if __name__ == "__main__":
    ret = main()
    log.info(f'Closed with return code {ret}')
    sys.exit(ret)
