import logging
import traceback
from asyncio import CancelledError, Task, create_task, current_task
from collections.abc import Callable, Coroutine
from typing import Final

from .protocols import DeviceProto


TASKS: Final[set[Task]] = set()

log = logging.getLogger('Tasks')


class Task:
    def __init__(self, coro: Callable[[], Coroutine], *, name: str):
        self._coro: Final = coro
        self._name: Final = name

        self._task: Task | None = None

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
        log.error(f'Error in {self._task._name:s}')
        for line in traceback.format_exc().splitlines():
            log.error(line)


class DeviceTask(Task):
    def __init__(self, device: DeviceProto, coro: Callable[[], Coroutine], *, name: str):
        super().__init__(coro, name=name)

        self._device: Final = device

    def process_exception(self, e: Exception):
        self._device.on_error(e)
