import asyncio
import logging
import platform
import sys
import traceback
import typing

from sml2mqtt._args import get_command_line_args
from sml2mqtt._log import setup_log
from sml2mqtt._signals import add_shutdown_handler, get_ret_code, shutdown_with_exception
from sml2mqtt.config import CONFIG
from sml2mqtt.mqtt import connect
from sml2mqtt.sml_device import Device


async def a_main():
    await connect()
    await asyncio.sleep(0.1)  # Wait till mqtt is connected

    # Create devices for port
    try:
        for k in CONFIG.devices:
            await Device.create(k.device, k.timeout, k.skip)
    except Exception as e:
        shutdown_with_exception(e)


def main() -> typing.Union[int, str]:
    args = get_command_line_args()
    log = logging.getLogger('sml2mqtt')

    CONFIG.load(args.config)
    setup_log()

    # This is needed to make asyncmqtt work
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Add possibility to stop program with Ctrl + c
    add_shutdown_handler()

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(a_main())
        loop.run_forever()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    return get_ret_code()


if __name__ == "__main__":
    sys.exit(main())
