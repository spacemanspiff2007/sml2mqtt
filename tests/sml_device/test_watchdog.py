from __future__ import annotations

import asyncio
from unittest.mock import Mock

from sml2mqtt.sml_device import DeviceStatus, SmlDevice
from sml2mqtt.sml_device.watchdog import Watchdog


def get_watchdog() -> tuple[Mock, Watchdog]:
    p = Mock()
    p.name = 'test'
    m = p.on_timeout
    m.assert_not_called()

    w = Watchdog(p).set_timeout(0.1)
    return m, w


async def test_watchdog_expire():

    m, w = get_watchdog()
    w.start()

    await asyncio.sleep(0.15)
    m.assert_called_once()
    w.feed()
    await asyncio.sleep(0.15)
    assert m.call_count == 2

    await w.cancel_and_wait()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)


async def test_watchdog_no_expire():

    m, w = get_watchdog()
    w.start()

    for _ in range(4):
        w.feed()
        await asyncio.sleep(0.06)

    m.assert_not_called()

    await w.cancel_and_wait()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)


async def test_watchdog_setup_and_feed(sml_data_1):

    obj = SmlDevice('test')
    obj.frame_handler = obj.process_frame
    obj.sml_values.set_skipped(
        '0100000009ff', '0100010800ff', '0100010801ff', '0100010802ff', '0100020800ff',
        '0100100700ff', '0100240700ff', '0100380700ff', '01004c0700ff'
    )
    obj.watchdog.set_timeout(0.2)

    await obj.start()
    assert obj.status == DeviceStatus.STARTUP

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    for _ in range(5):
        await asyncio.sleep(0.15)
        obj.on_source_data(sml_data_1)
        assert obj.status == DeviceStatus.OK

    await asyncio.sleep(0.3)
    assert obj.status == DeviceStatus.MSG_TIMEOUT

    await obj.cancel_and_wait()
