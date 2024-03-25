from aiohttp import BasicAuth

from sml2mqtt.config.source import HttpSourceSettings
from sml2mqtt.sml_source import create_source
from sml2mqtt.sml_source.http import HttpSource


async def test_create_http_no_auth(device_mock):
    cfg = HttpSourceSettings(type='http', url='http://localhost/a', interval=3, timeout=6)
    obj = await create_source(device_mock, cfg)

    assert isinstance(obj, HttpSource)
    assert obj.url == 'http://localhost/a'
    assert obj.auth is None
    assert obj.interval == 3

    device_mock.on_source_data.assert_not_called()
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_not_called()


async def test_create_http_auth(device_mock):
    cfg = HttpSourceSettings(type='http', url='http://localhost/a', interval=3, timeout=6, user='u', password='p')
    obj = await create_source(device_mock, cfg)

    assert isinstance(obj, HttpSource)
    assert obj.url == 'http://localhost/a'
    assert obj.auth == BasicAuth('u', 'p')
    assert obj.interval == 3

    device_mock.on_source_data.assert_not_called()
    device_mock.on_source_failed.assert_not_called()
    device_mock.on_error.assert_not_called()
