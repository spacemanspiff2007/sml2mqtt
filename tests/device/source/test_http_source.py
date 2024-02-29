from asyncio import sleep
from typing import Tuple
from unittest.mock import call, Mock

from aiohttp import ClientTimeout
from aioresponses import aioresponses

from sml2mqtt.device import DeviceStatus
from sml2mqtt.device.sml_sources.sml_http import HttpSource


def get_source() -> Tuple[HttpSource, Mock, Mock]:
    url = 'http:192.168.0.55:99999'
    source = HttpSource(Mock(), url, interval=0, auth=None, timeout=ClientTimeout(0.5))

    status_mock: Mock = source.device.set_status
    status_mock.assert_not_called()
    data_mock: Mock = source.device.serial_data_read
    data_mock.assert_not_called()

    return source, status_mock, data_mock


async def test_ok(sml_data_1):
    source, status_mock, data_mock = get_source()

    with aioresponses() as m:
        m.get(source.url, body=sml_data_1)

        await source.start()

        while not data_mock.called:
            await sleep(0)

        await source.stop()
        await source.wait_for_stop()

    status_mock.assert_called_once_with(DeviceStatus.STARTUP)
    data_mock.assert_called_once_with(sml_data_1)


async def test_400(sml_data_1):
    source, status_mock, data_mock = get_source()

    with aioresponses() as m:
        m.get(source.url, status=404)

        await source.start()

        while status_mock.call_count < 2:
            await sleep(0)

        await source.stop()
        await source.wait_for_stop()

    assert status_mock.call_args_list == [call(DeviceStatus.STARTUP), call(DeviceStatus.ERROR)]
    data_mock.assert_not_called()
