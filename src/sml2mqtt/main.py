import asyncio
import logging
import platform
import signal
import sys
import traceback
import typing

from sml2mqtt._args import get_command_line_args
from sml2mqtt._log import setup_log
from sml2mqtt.config import CONFIG
from sml2mqtt.mqtt import connect
from sml2mqtt.sml_device import Device

log = logging.getLogger('sml')


async def a_main():
    await connect()
    await asyncio.sleep(0.1)  # Wait till mqtt is connected

    readers = []
    for k in CONFIG.devices:
        d = await Device.create(k.device, k.skip)
        readers.append(asyncio.create_task(d.read()))

    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        for r in readers:
            r.cancel()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    await asyncio.gather(*readers)


def main() -> typing.Union[int, str]:
    args = get_command_line_args()
    log = logging.getLogger('sml')

    CONFIG.load(args.config)
    setup_log()

    # This is needed to make asyncmqtt work
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(a_main())
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
