# flake8: noqa: E501
import asyncio
import logging
from binascii import a2b_hex

from sml2mqtt import CMD_ARGS
from sml2mqtt.device import Device


async def test_serial_data(device: Device, no_serial, caplog, test_data_1: bytes):
    caplog.set_level(logging.DEBUG)

    CMD_ARGS.analyze = True

    await device.serial_data_read(a2b_hex(test_data_1))

    msg = "\n".join(map(lambda x: x.msg, filter(lambda x: x.name == 'sml.mqtt.pub', caplog.records)))

    assert msg == \
        'testing/00000000000000000000/0100010800ff: 450.09189911 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100010801ff: 449.07489911 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100010802ff: 1.017 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100020800ff: 2.198 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100100700ff: 352.89 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100240700ff: 82.26 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/0100380700ff: 27.06 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/01004c0700ff: 243.57 (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/status: OK (QOS: 0, retain: False)\n' \
        'testing/00000000000000000000/status: SHUTDOWN (QOS: 0, retain: False)'

    msg = "\n".join(map(lambda x: x.msg, filter(lambda x: x.name == 'sml.device_url', caplog.records)))

    print(msg)

    assert msg == '''
Received Frame
 -> b'760501188e6162006200726500000101760101070000000000000b00000000000000000000010163687700760501188e626200620072650000070177010b000000000000000000000172620165002ec3f47a77078181c78203ff010101010445425a0177070100000009ff010101010b000000000000000000000177070100010800ff6401018001621e52fb690000000a7ac1bc170177070100010801ff0101621e52fb690000000a74b1ea770177070100010802ff0101621e52fb6900000000060fd1a00177070100020800ff6401018001621e52fb69000000000d19e1c00177070100100700ff0101621b52fe55000089d90177070100240700ff0101621b52fe55000020220177070100380700ff0101621b52fe5500000a9201770701004c0700ff0101621b52fe5500005f2501010163810200760501188e636200620072650000020171016325fc00'

<SmlMessage>
  transaction_id: 01188e61
  group_no      : 0
  abort_on_error: 0
  message_body <SmlOpenResponse>
    codepage   : None
    client_id  : None
    req_file_id: 000000000000
    server_id  : 00000000000000000000
    ref_time   : None
    sml_version: None
  crc16         : 26743
<SmlMessage>
  transaction_id: 01188e62
  group_no      : 0
  abort_on_error: 0
  message_body <SmlGetListResponse>
    client_id       : None
    sever_id        : 00000000000000000000
    list_name       : None
    act_sensor_time : 3064820
    val_list:
      <SmlListEntry>
        obis           : 8181c78203ff (129-129:199.130.3*255)
        status         : None
        val_time       : None
        unit           : None
        scaler         : None
        value          : EBZ
        value_signature: None
        -> (Hersteller-Identifikation)
      <SmlListEntry>
        obis           : 0100000009ff (1-0:0.0.9*255)
        status         : None
        val_time       : None
        unit           : None
        scaler         : None
        value          : 00000000000000000000
        value_signature: None
        -> (Geräteeinzelidentifikation)
      <SmlListEntry>
        obis           : 0100010800ff (1-0:1.8.0*255)
        status         : 65920
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 45009189911
        value_signature: None
        -> 450091.89911Wh (Zählerstand Total)
      <SmlListEntry>
        obis           : 0100010801ff (1-0:1.8.1*255)
        status         : None
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 44907489911
        value_signature: None
        -> 449074.89911Wh (Zählerstand Tarif 1)
      <SmlListEntry>
        obis           : 0100010802ff (1-0:1.8.2*255)
        status         : None
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 101700000
        value_signature: None
        -> 1017.0Wh (Zählerstand Tarif 2)
      <SmlListEntry>
        obis           : 0100020800ff (1-0:2.8.0*255)
        status         : 65920
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 219800000
        value_signature: None
        -> 2198.0Wh
      <SmlListEntry>
        obis           : 0100100700ff (1-0:16.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 35289
        value_signature: None
        -> 352.89W (aktuelle Wirkleistung)
      <SmlListEntry>
        obis           : 0100240700ff (1-0:36.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 8226
        value_signature: None
        -> 82.26W (Wirkleistung L1)
      <SmlListEntry>
        obis           : 0100380700ff (1-0:56.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 2706
        value_signature: None
        -> 27.06W (Wirkleistung L2)
      <SmlListEntry>
        obis           : 01004c0700ff (1-0:76.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 24357
        value_signature: None
        -> 243.57W (Wirkleistung L3)
    list_signature  : None
    act_gateway_time: None
  crc16         : 33026
<SmlMessage>
  transaction_id: 01188e63
  group_no      : 0
  abort_on_error: 0
  message_body <SmlCloseResponse>
    global_signature: None
  crc16         : 9724


testing/00000000000000000000/0100010800ff (0100010800ff):
  raw value: 450.09189911
  pub value: 450.09189911
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100010801ff (0100010801ff):
  raw value: 449.07489911
  pub value: 449.07489911
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100010802ff (0100010802ff):
  raw value: 1.017
  pub value: 1.017
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100020800ff (0100020800ff):
  raw value: 2.198
  pub value: 2.198
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100100700ff (0100100700ff):
  raw value: 352.89
  pub value: 352.89
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100240700ff (0100240700ff):
  raw value: 82.26
  pub value: 82.26
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/0100380700ff (0100380700ff):
  raw value: 27.06
  pub value: 27.06
  filters:
    - <Every: 120>
    - <OnChange>

testing/00000000000000000000/01004c0700ff (01004c0700ff):
  raw value: 243.57
  pub value: 243.57
  filters:
    - <Every: 120>
    - <OnChange>
'''

    await asyncio.sleep(0.1)
