import logging

from smllib.reader import SmlFrame

from device.conftest import TestingDevice
from sml2mqtt import CMD_ARGS, CONFIG
from sml2mqtt.config.device import SmlDeviceConfig


async def test_frame_no_match_obis_id(device: TestingDevice, no_serial, caplog, monkeypatch,
                                      sml_frame_1: SmlFrame, sml_frame_1_analyze, ):
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(CMD_ARGS, 'analyze', True)

    device.testing_raise_on_status = False
    device.serial_data_read(sml_frame_1)

    msg = "\n".join(x.msg for x in caplog.records)

    assert msg == sml_frame_1_analyze + """
Found none of the following obis ids in the sml frame: 0100000009ff
Received Frame
 -> b'760500531efa620062007263010176010105001bb4fe0b0a0149534b0005020de272620165001bb32e620163a71400760500531efb620062007263070177010b0a0149534b0005020de2070100620affff72620165001bb32e757707010060320101010101010449534b0177070100600100ff010101010b0a0149534b0005020de20177070100010800ff65001c010401621e52ff650026bea90177070100020800ff0101621e52ff62000177070100100700ff0101621b52005301100101016350ba00760500531efc6200620072630201710163ba1900'

ERROR
testing/device_url/status: ERROR (QOS: 0, retain: False)"""


async def test_frame_no_config(device: TestingDevice, no_serial, caplog, monkeypatch,
                               sml_frame_1: SmlFrame, sml_frame_1_analyze, ):
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(CMD_ARGS, 'analyze', True)
    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100600100ff'])

    device.testing_raise_on_status = False
    device.serial_data_read(sml_frame_1)

    msg = "\n".join(x.msg for x in caplog.records)

    assert msg == sml_frame_1_analyze + """
Found obis id 0100600100ff in the sml frame
No configuration found for 0a0149534b0005020de2
Creating default value handler for 010060320101
Creating default value handler for 0100010800ff
Creating default value handler for 0100100700ff
testing/0a0149534b0005020de2/010060320101: ISK (QOS: 0, retain: False)
testing/0a0149534b0005020de2/0100010800ff: 253.9177 (QOS: 0, retain: False)
testing/0a0149534b0005020de2/0100100700ff: 272 (QOS: 0, retain: False)
OK
testing/0a0149534b0005020de2/status: OK (QOS: 0, retain: False)

testing/0a0149534b0005020de2/010060320101 (010060320101):
  raw value: ISK
  pub value: ISK
  filters:
    - <Every: 120>
    - <OnChange>

testing/0a0149534b0005020de2/0100010800ff (0100010800ff):
  raw value: 253.9177
  pub value: 253.9177
  filters:
    - <Every: 120>
    - <OnChange>

testing/0a0149534b0005020de2/0100100700ff (0100100700ff):
  raw value: 272
  pub value: 272
  filters:
    - <Every: 120>
    - <OnChange>

SHUTDOWN
testing/0a0149534b0005020de2/status: SHUTDOWN (QOS: 0, retain: False)"""


async def test_frame_with_config(device: TestingDevice, no_serial, caplog, monkeypatch,
                                 sml_frame_1: SmlFrame, sml_frame_1_analyze, ):
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(CMD_ARGS, 'analyze', True)
    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100600100ff'])
    monkeypatch.setitem(CONFIG.devices, '0a0149534b0005020de2', SmlDeviceConfig(
        skip=['010060320101']
    ))

    device.serial_data_read(sml_frame_1)

    msg = "\n".join(x.msg for x in caplog.records)

    assert msg == sml_frame_1_analyze + """
Found obis id 0100600100ff in the sml frame
Configuration found for 0a0149534b0005020de2
Creating default value handler for 0100010800ff
Creating default value handler for 0100100700ff
testing/0a0149534b0005020de2/0100010800ff: 253.9177 (QOS: 0, retain: False)
testing/0a0149534b0005020de2/0100100700ff: 272 (QOS: 0, retain: False)
OK
testing/0a0149534b0005020de2/status: OK (QOS: 0, retain: False)

testing/0a0149534b0005020de2/0100010800ff (0100010800ff):
  raw value: 253.9177
  pub value: 253.9177
  filters:
    - <Every: 120>
    - <OnChange>

testing/0a0149534b0005020de2/0100100700ff (0100100700ff):
  raw value: 272
  pub value: 272
  filters:
    - <Every: 120>
    - <OnChange>

SHUTDOWN
testing/0a0149534b0005020de2/status: SHUTDOWN (QOS: 0, retain: False)"""
