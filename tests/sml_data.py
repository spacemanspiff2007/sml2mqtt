from binascii import a2b_hex

import pytest
from smllib.reader import SmlStreamReader

from sml2mqtt.const import EnhancedSmlFrame, SmlFrameValues


@pytest.fixture
def sml_data_1():
    return a2b_hex(
        b'1B1B1B1B01010101760501188E6162006200726500000101760101070000000000000B000000000000000000000101636877007'
        b'60501188E626200620072650000070177010B000000000000000000000172620165002EC3F47A77078181C78203FF0101010104'
        b'45425A0177070100000009FF010101010B000000000000000000000177070100010800FF6401018001621E52FB690000000A7AC'
        b'1BC170177070100010801FF0101621E52FB690000000A74B1EA770177070100010802FF0101621E52FB6900000000060FD1A001'
        b'77070100020800FF6401018001621E52FB69000000000D19E1C00177070100100700FF0101621B52FE55000089D901770701002'
        b'40700FF0101621B52FE55000020220177070100380700FF0101621B52FE5500000A9201770701004C0700FF0101621B52FE5500'
        b'005F2501010163810200760501188E636200620072650000020171016325FC000000001B1B1B1B1A0356F5'
    )


@pytest.fixture
def sml_frame_1(stream_reader):
    frame = EnhancedSmlFrame(a2b_hex(
        b'760500531efa620062007263010176010105001bb4fe0b0a0149534b0005020de272620165001bb32e620163a71400760500531e'
        b'fb620062007263070177010b0a0149534b0005020de2070100620affff72620165001bb32e757707010060320101010101010449'
        b'534b0177070100600100ff010101010b0a0149534b0005020de20177070100010800ff65001c010401621e52ff650026bea90177'
        b'070100020800ff0101621e52ff62000177070100100700ff0101621b52005301100101016350ba00760500531efc620062007263'
        b'0201710163ba1900'
    ))

    stream_reader.add(frame)
    return frame


@pytest.fixture
def sml_frame_2(stream_reader):
    frame = EnhancedSmlFrame(a2b_hex(
        b'7605065850a66200620072630101760107ffffffffffff05021d70370b0a014c475a0003403b4972620165021d7707016326de'
        b'007605065850a762006200726307017707ffffffffffff0b0a014c475a0003403b49070100620affff72620165021d77077577'
        b'0701006032010101010101044c475a0177070100600100ff010101010b0a014c475a0003403b490177070100010800ff65001c'
        b'010472620165021d7707621e52ff690000000003152c450177070100020800ff0172620165021d7707621e52ff690000000000'
        b'0000000177070100100700ff0101621b52005900000000000000fb010101637264007605065850a86200620072630201710163'
        b'1c8c00'
    ))

    stream_reader.add(frame)
    return frame


@pytest.fixture
def sml_data_1_analyze(sml_data_1):
    r = SmlStreamReader()
    r.add(sml_data_1)
    frame = r.get_frame()   # type: EnhancedSmlFrame | None
    return '\n'.join(frame.get_analyze_str())


@pytest.fixture
def sml_frame_1_values(sml_frame_1):
    values = sml_frame_1.get_obis()
    return SmlFrameValues.create(0, values)


@pytest.fixture
def sml_frame_1_analyze(sml_frame_1):
    return '\n'.join(sml_frame_1.get_analyze_str())


@pytest.fixture
def sml_frame_2_values(sml_frame_2):
    values = sml_frame_2.get_obis()
    return SmlFrameValues.create(0, values)


@pytest.fixture
def sml_frame_2_analyze(sml_frame_2):
    return '\n'.join(sml_frame_2.get_analyze_str())


@pytest.fixture
def sml_data_1_analyze() -> str:
    return '''
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
        -> 450091.89911Wh (Zählerstand Bezug Total)
      <SmlListEntry>
        obis           : 0100010801ff (1-0:1.8.1*255)
        status         : None
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 44907489911
        value_signature: None
        -> 449074.89911Wh (Zählerstand Bezug Tarif 1)
      <SmlListEntry>
        obis           : 0100010802ff (1-0:1.8.2*255)
        status         : None
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 101700000
        value_signature: None
        -> 1017.0Wh (Zählerstand Bezug Tarif 2)
      <SmlListEntry>
        obis           : 0100020800ff (1-0:2.8.0*255)
        status         : 65920
        val_time       : None
        unit           : 30
        scaler         : -5
        value          : 219800000
        value_signature: None
        -> 2198.0Wh (Zählerstand Einspeisung Total)
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
        -> 82.26W (Summenwirkleistung L1)
      <SmlListEntry>
        obis           : 0100380700ff (1-0:56.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 2706
        value_signature: None
        -> 27.06W (Summenwirkleistung L2)
      <SmlListEntry>
        obis           : 01004c0700ff (1-0:76.7.0*255)
        status         : None
        val_time       : None
        unit           : 27
        scaler         : -2
        value          : 24357
        value_signature: None
        -> 243.57W (Summenwirkleistung L3)
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
'''
