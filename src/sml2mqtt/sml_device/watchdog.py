from __future__ import annotations

from asyncio import Event, TimeoutError, wait_for
from typing import TYPE_CHECKING, Final

from ..const import DeviceTask


if TYPE_CHECKING:
    from .sml_device import SmlDevice


class Watchdog:
    def __init__(self, device: SmlDevice) -> None:
        self._timeout: float = -1
        self.device: Final = device

        self._event: Final = Event()
        self._task: Final  = DeviceTask(device, self._wd_task, name=f'Watchdog Task {self.device.name:s}')

    def start(self) -> None:
        self._task.start()

    def cancel(self) -> None:
        self._task.cancel()

    async def cancel_and_wait(self):
        return await self._task.cancel_and_wait()

    def set_timeout(self, timeout: float):
        if timeout < 0.1:
            raise ValueError()
        self._timeout = timeout
        return self

    def feed(self) -> None:
        self._event.set()

    async def _wd_task(self) -> None:
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
                self.device.on_error(e)
