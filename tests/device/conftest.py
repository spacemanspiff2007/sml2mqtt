from typing import Union

import pytest
from smllib import SmlFrame, SmlStreamReader

import sml2mqtt.device_old.sml_device
import sml2mqtt.device_old.sml_sources.sml_serial
from sml2mqtt import CMD_ARGS
from sml2mqtt.config.config import PortSourceSettings
from sml2mqtt.device_old import Device, DeviceStatus
from sml2mqtt.mqtt import MqttObj, patch_analyze


@pytest.fixture()
def sml_stream(monkeypatch):

    async def create_reader_source(settings, device: 'sml2mqtt.device.Device'):
        device.stream = TestingStreamReader(device.stream)
        return device.stream

    monkeypatch.setattr(sml2mqtt.device.sml_sources, 'create_source', create_reader_source)
    monkeypatch.setattr(sml2mqtt.device.sml_sources.setup, 'create_source', create_reader_source)
    return None


@pytest.fixture(autouse=True)
def clean_devices(monkeypatch):
    monkeypatch.setattr(sml2mqtt.device.sml_device, 'ALL_DEVICES', {})
    return None


class TestingStreamReader:
    def __init__(self, reader: SmlStreamReader):
        self.reader = reader
        self.data = None
        self.is_started = False

    def add(self, data: Union[SmlFrame, bytes]):
        if isinstance(data, SmlFrame):
            self.data = data
            self.reader.clear()
        else:
            self.data = None
            self.reader.add(data)

    def clear(self):
        self.reader.clear()

    def get_frame(self):
        assert self.is_started

        if self.data is None:
            return self.reader.get_frame()
        return self.data

    async def start(self):
        assert not self.is_started
        self.is_started = True

    async def stop(self):
        assert self.is_started
        self.is_started = False

    async def wait_for_stop(self):
        return None


class TestingDevice(Device):

    def __init__(self, /, logger_name: str, device_id: str, timeout: float, mqtt_device: MqttObj):
        super().__init__(logger_name, device_id, timeout, mqtt_device)

        self.stream: TestingStreamReader
        self.testing_raise_on_status = True

    def set_status(self, new_status: DeviceStatus) -> bool:
        if new_status is DeviceStatus.ERROR and self.testing_raise_on_status:
            raise
        return super().set_status(new_status)


@pytest.fixture()
async def device(sml_stream, monkeypatch):
    device_url = 'device_url'

    mqtt_base = MqttObj('testing', 0, False).update()
    monkeypatch.setattr(sml2mqtt.mqtt, 'BASE_TOPIC', mqtt_base)

    obj = await TestingDevice.create(PortSourceSettings(url=device_url))

    return obj


@pytest.fixture()
def arg_analyze(monkeypatch):
    monkeypatch.setattr(CMD_ARGS, 'analyze', True)
    patch_analyze()

    yield None

    module = sml2mqtt.mqtt.mqtt_obj
    assert hasattr(module, 'pub_func')
    module.pub_func = module.publish
