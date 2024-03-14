from aiohttp import ClientTimeout
from aioresponses import aioresponses
from helper import wait_for_call

from sml2mqtt.sml_source.http import HttpSource


async def test_200(sml_data_1, device_mock):

    source = HttpSource(device_mock, 'http:localhost:99999', interval=0, auth=None, timeout=ClientTimeout(0.5))

    with aioresponses() as m:
        m.get(source.url, body=sml_data_1)

        await source.start()
        try:
            await wait_for_call(device_mock.on_source_data, 1)
        finally:
            await source.stop()

    device_mock.on_source_data.assert_called_once_with(sml_data_1)
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_not_called()


async def test_400(device_mock):
    source = HttpSource(device_mock, 'http:localhost:99999', interval=0, auth=None, timeout=ClientTimeout(0.5))

    with aioresponses() as m:
        m.get(source.url, status=404)

        await source.start()
        try:
            await wait_for_call(device_mock.on_error, 1)
        finally:
            await source.stop()

    device_mock.on_source_data.assert_not_called()
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_called_once()
