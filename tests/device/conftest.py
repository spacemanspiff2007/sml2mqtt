from unittest.mock import AsyncMock, Mock

import pytest

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


@pytest.fixture()
async def device(no_serial):
    device_url = 'device_url'

    mqtt_base = MqttObj('testing', 0, False).update()
    mqtt_device = mqtt_base.create_child(device_url)

    obj = await Device.create(PortSettings(url=device_url), 1, set(), mqtt_device)

    # Wrapper so we see the traceback in the tests
    def wrapper(func):
        def raise_exception_on_error(status: DeviceStatus):
            if status is status.ERROR:
                raise
            func(status)
        return raise_exception_on_error

    assert hasattr(obj, 'set_status')
    obj.set_status = wrapper(obj.set_status)

    return obj
