from __future__ import annotations

from typing import TYPE_CHECKING, Final

from sml2mqtt.runtime import do_shutdown

from .device_status import DeviceStatus


if TYPE_CHECKING:
    from . import SmlDevice


class SmlDevices:
    def __init__(self) -> None:
        self._devices: tuple[SmlDevice, ...] = ()

    def add_device(self, device: SmlDevice) -> SmlDevice:
        for existing in self._devices:
            if existing.name == device.name:
                msg = f'Device {device.name:s} does already exist!'
                raise ValueError(msg)
        self._devices = (*self._devices, device)
        return device

    async def start(self) -> None:
        for device in self._devices:
            await device.start()

    async def cancel_and_wait(self) -> None:
        for device in self._devices:
            await device.cancel_and_wait()

    def check_status(self):
        if any(device.status in (DeviceStatus.SOURCE_FAILED, DeviceStatus.SHUTDOWN) for device in self._devices):
            return do_shutdown()

        if all(device.status.is_shutdown_status() for device in self._devices):
            return do_shutdown()

        return None

    def __len__(self) -> int:
        return len(self._devices)


ALL_DEVICES: Final = SmlDevices()
