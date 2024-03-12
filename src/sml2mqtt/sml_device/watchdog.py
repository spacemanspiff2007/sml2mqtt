from __future__ import annotations

from asyncio import Event, Task, TimeoutError, create_task, current_task, wait_for
from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    from .sml_device import SmlDevice


class Watchdog:
    def __init__(self, device: SmlDevice):
        self._timeout: float = -1
        self.device: Final = device

        self._event: Final = Event()
        self._task: Task | None = None

    async def start(self):
        assert self._timeout > 0
        assert self._task is None
        self._task = create_task(self._wd_task(), name=f'Watchdog {self.device.name:s}')

    async def stop(self):
        if self._task is not None:
            self._task.cancel()
            self._task = None

    def set_timeout(self, timeout: float):
        if timeout < 0.1:
            raise ValueError()
        self._timeout = timeout
        return self

    def feed(self):
        self._event.set()

    async def _wd_task(self):
        task = current_task()

        try:
            make_call = True
            while True:
                self._event.clear()

                try:
                    await wait_for(self._event.wait(), self._timeout)
                    make_call = True
                    continue
                except TimeoutError:
                    pass

                # callback only once!
                if not make_call:
                    continue
                make_call = False

                try:
                    self.device.on_timeout()
                except Exception as e:
                    self.device.on_source_error(e)

        except Exception as e:
            self.device.on_source_error(e)
        finally:
            if task is self._task:
                self._task = None
