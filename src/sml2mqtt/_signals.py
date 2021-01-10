import logging
import signal
from asyncio import create_task, get_event_loop, sleep
from typing import Optional, Union

log = logging.getLogger('sml2mqtt')
error_text: Optional[str] = None


async def stop_loop():
    await sleep(0.1)
    get_event_loop().stop()


def shutdown_with_exception(e: Exception):
    global error_text
    error_text = str(e)

    log.error(error_text)
    create_task(stop_loop())


def get_ret_code() -> Union[int, str]:
    if error_text is not None:
        return error_text
    return 0


def shutdown_handler(sig, frame):
    print('Shutting down ...')
    log.info('Shutting down ...')
    create_task(stop_loop())


def add_shutdown_handler():
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
