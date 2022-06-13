import asyncio
import logging

from smllib.reader import SmlFrame

from sml2mqtt import CONFIG
from sml2mqtt.config.device import SmlDeviceConfig
from sml2mqtt.device import Device


async def test_frame_no_shortcut(device: Device, no_serial, caplog, sml_frame_2: SmlFrame, monkeypatch, no_mqtt):
    caplog.set_level(logging.DEBUG)

    monkeypatch.setitem(CONFIG.devices, 'device_url', SmlDeviceConfig(
        mqtt={'topic': 'xxxx'}
    ))

    await device.process_frame(sml_frame_2)
    await asyncio.sleep(0.01)

    assert no_mqtt == [
        ('testing/xxxx/010060320101', 'LGZ', 0, False),
        ('testing/xxxx/0100600100ff', '0a014c475a0003403b49', 0, False),
        ('testing/xxxx/0100010800ff', 5171.9237, 0, False),
        ('testing/xxxx/0100100700ff', 251, 0, False),
        ('testing/xxxx/status', 'OK', 0, False)
    ]
