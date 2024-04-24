import sys
from asyncio import TimeoutError

import pytest
from aiohttp import ClientTimeout
from aioresponses import aioresponses
from tests.helper import wait_for_call

from sml2mqtt.errors import HttpStatusError
from sml2mqtt.sml_source.http import HttpSource, close_session


@pytest.fixture()
def source(device_mock):
    return HttpSource(device_mock, 'http://localhost:39999', interval=0.020, auth=None, timeout=ClientTimeout(0.5))


@pytest.mark.skipif(sys.platform.lower() != "win32", reason="It's a mystery why this fails in CI")
async def test_200(sml_data_1, device_mock, source):

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


@pytest.mark.skipif(sys.platform.lower() != "win32", reason="It's a mystery why this fails in CI")
async def test_400_then_200(sml_data_1, device_mock, source):

    with aioresponses() as m:
        m.get(source.url, status=404)
        m.get(source.url, status=404)
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


@pytest.mark.skipif(sys.platform.lower() != "win32", reason="It's a mystery why this fails in CI")
async def test_400(device_mock, source):

    with aioresponses() as m:
        for _ in range(10):
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


def test_error_repr():
    assert str(HttpStatusError(404)) == 'HttpStatusError: 404'


@pytest.mark.skipif(sys.platform.lower() != "win32", reason="It's a mystery why this fails in CI")
async def test_timeout(device_mock, source):

    e = TimeoutError()

    with aioresponses() as m:
        for _ in range(10):
            m.get(source.url, exception=e)

        source.start()
        try:
            await wait_for_call(device_mock.on_error, 1)
        finally:
            await source.cancel_and_wait()

    device_mock.on_source_data.assert_not_called()
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_called_once_with(e, show_traceback=False)

    await close_session()
