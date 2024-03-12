from binascii import a2b_hex

import pytest
from smllib.reader import SmlFrame

import sml2mqtt.mqtt.mqtt_obj
from sml2mqtt.const import SmlFrameValues


class PatchedMonotonic:
    def __init__(self):
        self._now: int | float = 0
        self._mp = pytest.MonkeyPatch()

    def _get_monotonic(self):
        return self._now

    def patch_name(self, target: str):
        self._mp.setattr(target, self._get_monotonic)

    def patch(self, target: str | object, name: str | object):
        self._mp.setattr(target, name, value=self._get_monotonic)

    def undo(self):
        self._mp.undo()

    def add(self, secs: float):
        self._now += secs

    def set(self, secs: float):
        self._now = secs


@pytest.fixture()
def monotonic():
    p = PatchedMonotonic()

    p.patch_name('sml2mqtt.sml_value.operations.filter.monotonic')

    try:
        yield p
    finally:
        p.undo()


@pytest.fixture()
def no_mqtt(monkeypatch):

    pub_list = []

    def pub_func(topic: str, value, qos: int, retain: bool):
        pub_list.append((topic, value, qos, retain))

    monkeypatch.setattr(sml2mqtt.mqtt.mqtt_obj, 'pub_func', pub_func)
    return pub_list


@pytest.fixture()
def sml_data_1():
    data = b'1B1B1B1B01010101760501188E6162006200726500000101760101070000000000000B000000000000000000000101636877007' \
           b'60501188E626200620072650000070177010B000000000000000000000172620165002EC3F47A77078181C78203FF0101010104' \
           b'45425A0177070100000009FF010101010B000000000000000000000177070100010800FF6401018001621E52FB690000000A7AC' \
           b'1BC170177070100010801FF0101621E52FB690000000A74B1EA770177070100010802FF0101621E52FB6900000000060FD1A001' \
           b'77070100020800FF6401018001621E52FB69000000000D19E1C00177070100100700FF0101621B52FE55000089D901770701002' \
           b'40700FF0101621B52FE55000020220177070100380700FF0101621B52FE5500000A9201770701004C0700FF0101621B52FE5500' \
           b'005F2501010163810200760501188E636200620072650000020171016325FC000000001B1B1B1B1A0356F5'

    yield data


@pytest.fixture()
def sml_frame_1():
    data = b'760500531efa620062007263010176010105001bb4fe0b0a0149534b0005020de272620165001bb32e620163a71400760500531e' \
           b'fb620062007263070177010b0a0149534b0005020de2070100620affff72620165001bb32e757707010060320101010101010449' \
           b'534b0177070100600100ff010101010b0a0149534b0005020de20177070100010800ff65001c010401621e52ff650026bea90177' \
           b'070100020800ff0101621e52ff62000177070100100700ff0101621b52005301100101016350ba00760500531efc620062007263' \
           b'0201710163ba1900'

    return SmlFrame(a2b_hex(data))


@pytest.fixture()
def sml_frame_2():
    data = b'7605065850a66200620072630101760107ffffffffffff05021d70370b0a014c475a0003403b4972620165021d7707016326de' \
           b'007605065850a762006200726307017707ffffffffffff0b0a014c475a0003403b49070100620affff72620165021d77077577' \
           b'0701006032010101010101044c475a0177070100600100ff010101010b0a014c475a0003403b490177070100010800ff65001c' \
           b'010472620165021d7707621e52ff690000000003152c450177070100020800ff0172620165021d7707621e52ff690000000000' \
           b'0000000177070100100700ff0101621b52005900000000000000fb010101637264007605065850a86200620072630201710163' \
           b'1c8c00'

    return SmlFrame(a2b_hex(data))

@pytest.fixture()
def sml_frame_values_1(sml_frame_1):
    values = sml_frame_1.get_obis()
    return SmlFrameValues.create(0, values)

@pytest.fixture()
def sml_frame_1_analyze():
    msg = """
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
    server_id       : 0a0149534b0005020de2
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
        -> 0.0Wh (Wirkenergie Total)
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
"""
    return msg
