from aiohttp import ClientTimeout
from aioresponses import aioresponses
from helper import wait_for_call
from sml2mqtt.runtime import do_shutdown_async

from sml2mqtt.sml_source.http import HttpSource
from sml2mqtt.sml_source.http import close_session


async def test_200(sml_data_1, device_mock):

    source = HttpSource(device_mock, 'http:localhost:99999', interval=0, auth=None, timeout=ClientTimeout(0.5))

    with aioresponses() as m:
        m.get(source.url, body=sml_data_1)

        source.start()
        try:
            await wait_for_call(device_mock.on_source_data, 1)
        finally:
            await source.cancel_and_wait()

    device_mock.on_source_data.assert_called_once_with(sml_data_1)
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_not_called()

    await close_session()


async def test_400(device_mock):
    source = HttpSource(device_mock, 'http:localhost:99999', interval=0, auth=None, timeout=ClientTimeout(0.5))

    with aioresponses() as m:
        m.get(source.url, status=404)

        source.start()
        try:
            await wait_for_call(device_mock.on_error, 1)
        finally:
            await source.cancel_and_wait()

    device_mock.on_source_data.assert_not_called()
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_called_once()

    await close_session()
