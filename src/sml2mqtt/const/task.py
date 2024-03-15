from __future__ import annotations

import logging
import traceback
from asyncio import CancelledError, create_task, current_task
from asyncio import Task as asyncio_Task
from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    from .protocols import DeviceProto
    from collections.abc import Callable, Coroutine


TASKS: Final[set[asyncio_Task]] = set()

log = logging.getLogger('Tasks')


async def wait_for_tasks():
    while True:
        for task in TASKS:
            if not task.done():
                await task
                break
        else:
            break


class Task:
    def __init__(self, coro: Callable[[], Coroutine], *, name: str):
        self._coro: Final = coro
        self._name: Final = name

        self._task: asyncio_Task | None = None

    async def start(self):
        assert self._task is None
        self._task = task = create_task(self._coro(), name=self._name)

        TASKS.add(task)
        task.add_done_callback(TASKS.discard)

    async def stop(self):
        if self._task is None:
            return None

        task = self._task
        self._task = None

        task.cancel()

        try:  # noqa: SIM105
            await task
        except CancelledError:
            pass

    async def _wrapper(self):
        task = current_task()

        try:
            await self._coro()
        except Exception as e:
            self.process_exception(e)
        finally:
            if task is self._task:
                self._task = None

    def process_exception(self, e: Exception):
        log.error(f'Error in {self._name:s}')
        for line in traceback.format_exc().splitlines():
            log.error(line)


class DeviceTask(Task):
    def __init__(self, device: DeviceProto, coro: Callable[[], Coroutine], *, name: str):
        super().__init__(coro, name=name)
        self._device: Final = device

    def process_exception(self, e: Exception):
        super().process_exception(e)
        self._device.on_source_failed(f'Task crashed: {e}')
