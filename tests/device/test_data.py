import logging
from asyncio import Task
from binascii import a2b_hex
from unittest.mock import Mock

from serial_asyncio import SerialTransport

from sml2mqtt.device import Device
from sml2mqtt.device.sml_sources.sml_serial import SerialSource


async def test_serial_data(device: Device, caplog, sml_data_1: bytes, arg_analyze):
    caplog.set_level(logging.DEBUG)

    # we want to test incoming data from the serial port
    device.sml_source = SerialSource()
    device.sml_source.device = device
    device.sml_source.transport = Mock(SerialTransport)
    device.sml_source._task = Mock(Task)

    await device.stream.start()

    chunk_size = 100
    for i in range(0, len(sml_data_1), chunk_size):
        device.sml_source.data_received(a2b_hex(sml_data_1[i: i + chunk_size]))

    msg = "\n".join(x.msg for x in filter(lambda x: x.name == 'sml.mqtt.pub', caplog.records))

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

    msg = "\n".join(x.msg for x in filter(lambda x: x.name == 'sml.device_url', caplog.records))

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
    server_id       : 00000000000000000000
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
        -> 2198.0Wh (Wirkenergie Total)
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

Found obis id 0100000009ff in the sml frame
No configuration found for 00000000000000000000
Creating default value handler for 0100010800ff
Creating default value handler for 0100010801ff
Creating default value handler for 0100010802ff
Creating default value handler for 0100020800ff
Creating default value handler for 0100100700ff
Creating default value handler for 0100240700ff
Creating default value handler for 0100380700ff
Creating default value handler for 01004c0700ff

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
