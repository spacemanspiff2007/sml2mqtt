import asyncio
from binascii import a2b_hex
from unittest.mock import Mock

from sml2mqtt.config.config import PortSettings
from sml2mqtt.device import Device, DeviceStatus
from sml2mqtt.device.watchdog import Watchdog
from sml2mqtt.mqtt import MqttObj


async def test_watchdog_expire():

    m = Mock()
    m.assert_not_called()

    w = Watchdog(0.1, m)
    w.start()

    await asyncio.sleep(0.4)
    m.assert_called_once()
    w.feed()
    await asyncio.sleep(0.4)
    assert m.call_count == 2

    w.cancel()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)
    assert w.task is None


async def test_watchdog_no_expire():

    m = Mock()
    m.assert_not_called()

    w = Watchdog(0.1, m)
    w.start()
    for _ in range(4):
        w.feed()
        await asyncio.sleep(0.06)

    m.assert_not_called()

    w.cancel()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)
    assert w.task is None


async def test_watchdog_setup_and_feed(no_serial, sml_data_1):
    device_url = 'watchdog_test'

    mqtt_base = MqttObj('testing', 0, False).update()
    mqtt_device = mqtt_base.create_child(device_url)

    obj = await Device.create(PortSettings(url=device_url), 0.2, set(), mqtt_device)
    obj.start()
    assert obj.status == DeviceStatus.STARTUP

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    for _ in range(5):
        await asyncio.sleep(0.15)
        obj.serial_data_read(a2b_hex(sml_data_1))
        assert obj.status != DeviceStatus.MSG_TIMEOUT

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    async def cancel():
        obj.stop()

    await asyncio.gather(obj, cancel())
