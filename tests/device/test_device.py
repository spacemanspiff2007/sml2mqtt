import asyncio
from time import monotonic
from unittest.mock import Mock

from sml2mqtt.device import Device
from sml2mqtt.device.sml_sources.sml_serial import SerialSource
from sml2mqtt.mqtt import MqttObj


async def test_device_await(device: Device, caplog):
    device = Device('test_log', 'test_id', 1, MqttObj('testing', 0, False))
    device.sml_source = SerialSource()
    device.sml_source.url = 'test'
    device.sml_source.transport = Mock()
    device.sml_source.transport.is_closing = lambda: False
    await device.start()

    async def cancel():
        await asyncio.sleep(0.3)
        await device.stop()

    t = asyncio.create_task(cancel())
    start = monotonic()
    await asyncio.wait_for(device, 1)
    await t
    assert monotonic() - start < 0.4

    await asyncio.sleep(0.1)
