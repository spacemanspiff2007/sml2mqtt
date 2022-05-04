# flake8: noqa: E501

import logging

from smllib.reader import SmlFrame

from sml2mqtt import CMD_ARGS, CONFIG
from sml2mqtt.config.device import SmlDeviceConfig
from sml2mqtt.device import Device


async def test_frame_no_id(device: Device, no_serial, caplog, sml_frame_1: SmlFrame, monkeypatch):

    monkeypatch.setitem(CONFIG.devices, 'device_url', SmlDeviceConfig(
        mqtt={'topic': 'xxxx'}, skip={'010060320101', '0100600100ff'}
    ))

    caplog.set_level(logging.DEBUG)
    CMD_ARGS.analyze = True

    await device.process_frame(sml_frame_1)

    msg = "\n".join(map(lambda x: x.msg, caplog.records))

    assert msg == """
Received Frame
 -> b'760500531efa620062007263010176010105001bb4fe0b0a0149534b0005020de272620165001bb32e620163a71400760500531efb620062007263070177010b0a0149534b0005020de2070100620affff72620165001bb32e757707010060320101010101010449534b0177070100600100ff010101010b0a0149534b0005020de20177070100010800ff65001c010401621e52ff650026bea90177070100020800ff0101621e52ff62000177070100100700ff0101621b52005301100101016350ba00760500531efc6200620072630201710163ba1900'

<SmlMessage>
  transaction_id: 00531efa
  group_no      : 0
  abort_on_error: 0
  message_body <SmlOpenResponse>
    codepage   : None
    client_id  : None
    req_file_id: 001bb4fe
    server_id  : 0a0149534b0005020de2
    ref_time   : 1815342
    sml_version: 1
  crc16         : 42772
<SmlMessage>
  transaction_id: 00531efb
  group_no      : 0
  abort_on_error: 0
  message_body <SmlGetListResponse>
    client_id       : None
    sever_id        : 0a0149534b0005020de2
    list_name       : 0100620affff
    act_sensor_time : 1815342
    val_list:
      <SmlListEntry>
        obis           : 010060320101 (1-0:96.50.1*1)
        status         : None
        val_time       : None
        unit           : None
        scaler         : None
        value          : ISK
        value_signature: None
      <SmlListEntry>
        obis           : 0100600100ff (1-0:96.1.0*255)
        status         : None
        val_time       : None
        unit           : None
        scaler         : None
        value          : 0a0149534b0005020de2
        value_signature: None
      <SmlListEntry>
        obis           : 0100010800ff (1-0:1.8.0*255)
        status         : 1835268
        val_time       : None
        unit           : 30
        scaler         : -1
        value          : 2539177
        value_signature: None
        -> 253917.7Wh (Zählerstand Total)
      <SmlListEntry>
        obis           : 0100020800ff (1-0:2.8.0*255)
        status         : None
        val_time       : None
        unit           : 30
        scaler         : -1
        value          : 0
        value_signature: None
        -> 0.0Wh
      <SmlListEntry>
        obis           : 0100100700ff (1-0:16.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : 0
        value          : 272
        value_signature: None
        -> 272W (aktuelle Wirkleistung)
    list_signature  : None
    act_gateway_time: None
  crc16         : 20666
<SmlMessage>
  transaction_id: 00531efc
  group_no      : 0
  abort_on_error: 0
  message_body <SmlCloseResponse>
    global_signature: None
  crc16         : 47641

Creating default value handler for device_url/0100010800ff
testing/xxxx/0100010800ff: 253.9177 (QOS: 0, retain: False)
Creating default value handler for device_url/0100100700ff
testing/xxxx/0100100700ff: 272 (QOS: 0, retain: False)
OK
testing/xxxx/status: OK (QOS: 0, retain: False)

testing/xxxx/0100010800ff (0100010800ff):
  raw value: 253.9177
  pub value: 253.9177
  filters:
    - <Every: 120>
    - <OnChange>

testing/xxxx/0100100700ff (0100100700ff):
  raw value: 272
  pub value: 272
  filters:
    - <Every: 120>
    - <OnChange>

SHUTDOWN
testing/xxxx/status: SHUTDOWN (QOS: 0, retain: False)"""
