from asyncio import create_task, Event, Task, TimeoutError, wait_for
from typing import Any, Callable, Final, Optional


class Watchdog:
    def __init__(self, timeout: float, callback: Callable[[], Any]):
        if timeout <= 0:
            raise ValueError()
        self.timeout: Final = timeout
        self.callback: Final = callback
        self.event: Final = Event()
        self.task: Optional[Task] = None

    def start(self):
        if self.task is None:
            self.task = create_task(self.wd_task())

    def cancel(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None

    def feed(self):
        self.event.set()

    async def wd_task(self):
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
            self.task = None
