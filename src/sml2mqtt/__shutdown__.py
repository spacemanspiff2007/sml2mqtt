import signal
import traceback
from asyncio import create_task, Task
from typing import Dict, Optional, Type, Union

import sml2mqtt.mqtt
from sml2mqtt.__log__ import log
from sml2mqtt.errors import AllDevicesFailedError, DeviceSetupFailedError, InitialMqttConnectionFailedError

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
def _signal_handler_shutdown(sig, frame):
    set_return_code(0)
    do_shutdown()


def signal_handler_setup():
    signal.signal(signal.SIGINT, _signal_handler_shutdown)
    signal.signal(signal.SIGTERM, _signal_handler_shutdown)


# ----------------------------------------------------------------------------------------------------------------------
# Actual shutdown logic
# ----------------------------------------------------------------------------------------------------------------------
SHUTDOWN_TASK: Optional[Task] = None
SHUTDOWN_REQUESTED = False


def do_shutdown():
    global SHUTDOWN_TASK, SHUTDOWN_REQUESTED

    if SHUTDOWN_REQUESTED:
        return None

    if SHUTDOWN_TASK is None:
        SHUTDOWN_TASK = create_task(_shutdown_task())

    SHUTDOWN_REQUESTED = True


async def _shutdown_task():
    global SHUTDOWN_TASK

    try:
        print('Shutting down ...')
        log.info('Shutting down ...')

        sml2mqtt.mqtt.cancel()

        # once all devices are stopped the main loop will exit
        for device in sml2mqtt.device.sml_device.ALL_DEVICES.values():
            device.stop()
    finally:
        SHUTDOWN_TASK = None


# ----------------------------------------------------------------------------------------------------------------------
# shutdown helper
# ----------------------------------------------------------------------------------------------------------------------
def shutdown(e: Union[Exception, Type[Exception]]):
    global SHUTDOWN_TASK

    ret_map: Dict[int, Type[Exception]] = {
        10: DeviceSetupFailedError,
        11: InitialMqttConnectionFailedError,
        20: AllDevicesFailedError
    }

    log_traceback = True

    # get return code based on the error
    for ret_code, cls in ret_map.items():   # noqa: B007
        if isinstance(e, cls):
            log_traceback = False
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

    do_shutdown()
