from typing import Set, Union
from unittest.mock import AsyncMock, Mock

import pytest
from smllib import SmlFrame, SmlStreamReader

import sml2mqtt.device.sml_device
import sml2mqtt.device.sml_serial
from sml2mqtt.config.config import PortSettings
from sml2mqtt.device import Device, DeviceStatus
from sml2mqtt.mqtt import MqttObj


@pytest.fixture()
def no_serial(monkeypatch):

    m = Mock()
    m.create = AsyncMock()

    monkeypatch.setattr(sml2mqtt.device, 'SmlSerial', m)
    monkeypatch.setattr(sml2mqtt.device.sml_serial, 'SmlSerial', m)
    return m


@pytest.fixture(autouse=True)
def clean_devices(monkeypatch):
    monkeypatch.setattr(sml2mqtt.device.sml_device, 'ALL_DEVICES', {})
    return None


class TestingStreamReader:
    def __init__(self, reader: SmlStreamReader):
        self.reader = reader
        self.data = None

    def add(self, data: Union[SmlFrame, bytes]):
        if isinstance(data, SmlFrame):
            self.data = data
            self.reader.clear()
        else:
            self.data = None
            self.reader.add(data)

    def get_frame(self):
        if self.data is None:
            return self.reader.get_frame()
        return self.data


class TestingDevice(Device):

    def __init__(self, url: str, timeout: float, skip_values: Set[str], mqtt_device: MqttObj):
        super().__init__(url, timeout, skip_values, mqtt_device)
        self.stream = TestingStreamReader(self.stream)

        self.testing_raise_on_status = True

    def set_status(self, new_status: DeviceStatus) -> bool:
        if new_status is DeviceStatus.ERROR and self.testing_raise_on_status:
            raise
        return super().set_status(new_status)


@pytest.fixture()
async def device(no_serial):
    device_url = 'device_url'

    mqtt_base = MqttObj('testing', 0, False).update()
    mqtt_device = mqtt_base.create_child(device_url)

    obj = await TestingDevice.create(PortSettings(url=device_url), 1, set(), mqtt_device)

    return obj
