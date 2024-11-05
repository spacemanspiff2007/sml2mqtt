from __future__ import annotations

import logging.handlers
import signal
import traceback
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING, Final

from sml2mqtt.const import Task, create_task


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


log = logging.getLogger('sml.shutdown')


@dataclass(frozen=True)
class ShutdownObj:
    coro: Callable[[], Awaitable]
    msg: str

    async def do(self) -> None:
        try:
            log.debug(self.msg)
            await self.coro()
            log.debug(f'{self.msg:s} done!')
        except Exception as e:
            log.error(str(e))
            tb = traceback.format_exc().splitlines()
            for line in tb:
                log.error(line)


async def shutdown_coro() -> None:
    log.debug('Starting shutdown')
    for obj in SHUTDOWN_OBJS:
        await obj.do()
    log.debug('Shutdown complete')


def on_shutdown(coro: Callable[[], Awaitable], msg: str):
    global SHUTDOWN_OBJS
    for obj in SHUTDOWN_OBJS:
        if obj.coro == coro or obj.msg == msg:
            raise ValueError()
    SHUTDOWN_OBJS = (*SHUTDOWN_OBJS, ShutdownObj(coro, msg))


SHUTDOWN_OBJS: tuple[ShutdownObj, ...] = ()
SHUTDOWN_TASK: Final = Task(shutdown_coro, name='Shutdown Task')

SHUTDOWN_LOCK: Final = Lock()
SHUTDOWN_CALL: Task | None = None


async def do_shutdown_async() -> None:
    global SHUTDOWN_CALL

    try:
        if not SHUTDOWN_TASK.is_running:
            print('Shutting down ...')
            log.info('Shutting down ...')
            SHUTDOWN_TASK.start()
    finally:
        with SHUTDOWN_LOCK:
            SHUTDOWN_CALL = None


def do_shutdown():
    global SHUTDOWN_CALL

    with SHUTDOWN_LOCK:
        if SHUTDOWN_CALL is not None:
            return None
        SHUTDOWN_CALL = create_task(do_shutdown_async())


def _signal_handler_shutdown(sig, frame) -> None:
    do_shutdown()


def signal_handler_setup() -> None:
    signal.signal(signal.SIGINT, _signal_handler_shutdown)
    signal.signal(signal.SIGTERM, _signal_handler_shutdown)
