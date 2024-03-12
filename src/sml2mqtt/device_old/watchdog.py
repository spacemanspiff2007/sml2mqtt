from asyncio import CancelledError, create_task, current_task, Event, Task, TimeoutError, wait_for
from typing import Any, Callable, Final


class Watchdog:
    def __init__(self, timeout: float, callback: Callable[[], Any]):
        if timeout <= 0:
            raise ValueError()
        self.timeout: Final = timeout
        self.callback: Final = callback
        self.event: Final = Event()
        self.task: Task | None = None

    def start(self):
        assert self.task is None
        self.task = create_task(self.wd_task())

    def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None

    async def wait_for_stop(self):
        if self.task is None:
            return False
        try:
            await self.task
        except CancelledError:
            pass
        return True

    def feed(self):
        self.event.set()

    async def wd_task(self):
        task = current_task()

        try:
            make_call = True
            while True:
                self.event.clear()

                try:
                    await wait_for(self.event.wait(), self.timeout)
                    make_call = True
                    continue
                except TimeoutError:
                    pass

                # callback only once!
                if make_call:
                    make_call = False
                    self.callback()
        finally:
            if task == self.task:
                self.task = None
