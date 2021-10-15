import signal
import traceback
from asyncio import create_task, get_event_loop, sleep, Task
from typing import Dict, Optional, Type, Union

import sml2mqtt.mqtt
from sml2mqtt.__log__ import log
from sml2mqtt.errors import AllDevicesFailed, DeviceSetupFailed

# ----------------------------------------------------------------------------------------------------------------------
# Return code logic
# ----------------------------------------------------------------------------------------------------------------------
_RETURN_CODE: Optional[int] = None


def set_return_code(code: int):
    global _RETURN_CODE
    if _RETURN_CODE is None:
        _RETURN_CODE = code
    else:
        if _RETURN_CODE != code:
            log.debug(f'Return code is already set to {_RETURN_CODE}, skip setting {code}!')


def get_return_code() -> int:
    if _RETURN_CODE is None:
        log.warning('No return code set!')
        return 2
    return _RETURN_CODE


# ----------------------------------------------------------------------------------------------------------------------
# Signal handlers so we can shutdown gracefully
# ----------------------------------------------------------------------------------------------------------------------
def shutdown_handler(sig, frame):
    set_return_code(0)
    create_task(do_shutdown())


def setup_signal_handler():
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


# ----------------------------------------------------------------------------------------------------------------------
# Actual shutdown logic
# ----------------------------------------------------------------------------------------------------------------------
SHUTDOWN_TASK: Optional[Task] = None


async def do_shutdown():
    global SHUTDOWN_TASK

    try:
        print('Shutting down ...')
        log.info('Shutting down ...')

        for device in sml2mqtt.device.sml_device.ALL_DEVICES.values():
            device.shutdown()

        await sml2mqtt.mqtt.disconnect()
        await sleep(0.1)

        get_event_loop().stop()
    finally:
        SHUTDOWN_TASK = None


# ----------------------------------------------------------------------------------------------------------------------
# shutdown helper
# ----------------------------------------------------------------------------------------------------------------------
def shutdown(e: Union[Exception, Type[Exception]]):
    global SHUTDOWN_TASK

    ret_map: Dict[int, Type[Exception]] = {10: DeviceSetupFailed, 20: AllDevicesFailed}

    log_traceback = True

    # get return code based on the error
    for ret_code, cls in ret_map.items():
        if isinstance(e, cls):
            break

        if e is cls:
            log_traceback = False
            break
    else:
        ret_code = 1

    if log_traceback:
        for line in traceback.format_exc().splitlines():
            log.error(line)

    set_return_code(ret_code)

    if SHUTDOWN_TASK is None:
        SHUTDOWN_TASK = create_task(do_shutdown())
