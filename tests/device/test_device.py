import asyncio
from time import monotonic
from unittest.mock import Mock

from sml2mqtt.device import Device, SmlSerial
from sml2mqtt.mqtt import MqttObj


async def test_device_await(device: Device, no_serial, caplog):
    device = Device('test', 1, set(), MqttObj('testing', 0, False))
    device.serial = SmlSerial()
    device.serial.url = 'test'
    device.serial.transport = Mock()
    device.serial.transport.is_closing = lambda: False
    device.start()

    async def cancel():
        await asyncio.sleep(0.3)
        device.stop()

    t = asyncio.create_task(cancel())
    start = monotonic()
    await asyncio.wait_for(device, 1)
    await t
    assert monotonic() - start < 0.4

    await asyncio.sleep(0.1)
