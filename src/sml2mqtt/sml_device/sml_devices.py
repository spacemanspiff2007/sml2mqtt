from __future__ import annotations

from typing import TYPE_CHECKING, Final

from sml2mqtt.__shutdown__ import shutdown
from sml2mqtt.errors import DeviceFailedError

from .device_status import DeviceStatus


if TYPE_CHECKING:
    from . import SmlDevice


class SmlDevices:
    def __init__(self):
        self._devices: tuple[SmlDevice, ...] = ()

    def add_device(self, device: SmlDevice) -> SmlDevice:
        for existing in self._devices:
            if existing.name == device.name:
                msg = f'Device {device.name:s} does already exist!'
                raise ValueError(msg)
        self._devices = (*self._devices, device)
        return device

    async def start(self):
        for device in self._devices:
            await device.start()

    async def stop(self):
        for device in self._devices:
            await device.stop()

    def check_status(self):
        if any(device.status is DeviceStatus.SOURCE_FAILED for device in self._devices):
            return shutdown(DeviceFailedError)

        if all(device.status.is_shutdown_status() for device in self._devices):
            return shutdown(DeviceFailedError)

        return None


ALL_DEVICES: Final = SmlDevices()
