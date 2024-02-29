import asyncio
from binascii import a2b_hex
from unittest.mock import Mock

from sml2mqtt.config.config import PortSourceSettings
from sml2mqtt.device import Device, DeviceStatus
from sml2mqtt.device.watchdog import Watchdog


async def test_watchdog_expire():

    m = Mock()
    m.assert_not_called()

    w = Watchdog(0.1, m)
    w.start()

    await asyncio.sleep(0.15)
    m.assert_called_once()
    w.feed()
    await asyncio.sleep(0.15)
    assert m.call_count == 2

    w.stop()

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

    w.stop()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)
    assert w.task is None


async def test_watchdog_setup_and_feed(sml_stream, sml_data_1):
    device_url = 'watchdog_test'

    obj = await Device.create(PortSourceSettings(url=device_url, timeout=0.2))
    await obj.start()
    assert obj.status == DeviceStatus.STARTUP

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    for _ in range(5):
        await asyncio.sleep(0.15)
        obj.serial_data_read(a2b_hex(sml_data_1))
        assert obj.status == DeviceStatus.OK

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    await asyncio.gather(obj, obj.stop())
