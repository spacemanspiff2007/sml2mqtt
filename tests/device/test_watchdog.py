import asyncio
from unittest.mock import Mock

from sml2mqtt.device.watchdog import Watchdog


async def test_watchdog_expire():

    m = Mock()
    m.assert_not_called()

    w = Watchdog(0.1, m)
    w.start()
    await asyncio.sleep(0.4)
    m.assert_called_once()

    w.cancel()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)
    assert w.task is None


async def test_watchdog_no_expire():

    m = Mock()
    m.assert_not_called()

    w = Watchdog(0.1, m)
    w.start()
    for _ in range(3):
        w.feed()
        await asyncio.sleep(0.07)

    m.assert_not_called()

    w.cancel()

    # Assert that the task is properly canceled
    await asyncio.sleep(0.05)
    assert w.task is None
