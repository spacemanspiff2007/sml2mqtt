from __future__ import annotations

import logging
import traceback
from asyncio import CancelledError, Event, current_task
from asyncio import Task as asyncio_Task
from asyncio import create_task as asyncio_create_task
from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine

    from sml2mqtt.const.protocols import DeviceProto


TASKS: Final[set[asyncio_Task]] = set()

log = logging.getLogger('sml.tasks')


def create_task(coro: Coroutine, *, name: str | None = None):
    task = asyncio_create_task(coro, name=name)

    TASKS.add(task)
    task.add_done_callback(TASKS.discard)
    return task


async def wait_for_tasks() -> None:

    while True:
        for task in TASKS.copy():
            if task.done():
                continue

            # these are the asyncio tasks. Exceptions are handled either in Task or DeviceTask,
            # so we can not await the tasks here because that would raise the Exception.
            # That's why we use an event to signal that the task is done
            event = Event()
            task.add_done_callback(lambda x: event.set())
            await event.wait()
            break

        else:
            break

    log.debug('All tasks done')


class Task:
    def __init__(self, coro: Callable[[], Awaitable], *, name: str) -> None:
        self._coro: Final = coro
        self._name: Final = name

        self._task: asyncio_Task | None = None

    @property
    def is_running(self) -> bool:
        if (task := self._task) is None or task.cancelled():  # noqa: SIM103
            return False
        return True

    def start(self) -> None:
        if not self.is_running:
            self._task = create_task(self._wrapper(), name=self._name)

    def cancel(self) -> asyncio_Task | None:
        if (task := self._task) is None:
            return None

        task.cancel()
        return task

    async def cancel_and_wait(self) -> bool:
        if (task := self.cancel()) is None:
            return False

        try:  # noqa: SIM105
            await task
        except CancelledError:
            pass
        return True

    async def _wrapper(self) -> None:
        task = current_task()

        try:
            await self._coro()
        except Exception as e:
            self.process_exception(e)
        except CancelledError:
            pass
        finally:
            if task is self._task:
                self._task = None

            log.debug(f'{self._name:s} finished!')

    def process_exception(self, e: Exception) -> None:
        log.error(f'Error in {self._name:s}')
        for line in traceback.format_exc().splitlines():
            log.error(line)


class DeviceTask(Task):
    def __init__(self, device: DeviceProto, coro: Callable[[], Coroutine], *, name: str) -> None:
        super().__init__(coro, name=name)
        self._device: Final = device

    def process_exception(self, e: Exception) -> None:
        super().process_exception(e)
        self._device.on_source_failed(f'Task crashed: {e.__class__.__name__}')
