from binascii import a2b_hex

import pytest

from sml2mqtt import CONFIG
from sml2mqtt.sml_device import SmlDevice


@pytest.mark.ignore_log_errors()
async def test_frame_no_match_obis_id(no_mqtt, caplog, monkeypatch, sml_frame_2, arg_analyze, sml_frame_2_analyze):
    device = SmlDevice('device_name')
    device.frame_handler = device.analyze_frame

    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100000009ff', '01006001ffff'])

    device.on_source_data(None)

    msg = "\n".join(x.msg for x in caplog.records)

    assert msg.removeprefix(sml_frame_2_analyze) == '''
get_obis failed - try parsing frame
Found none of the following obis ids in the sml frame: 0100000009ff, 01006001ffff
Received Frame
 -> b'7605065850a66200620072630101760107ffffffffffff05021d70370b0a014c475a0003403b4972620165021d7707016326de007605065850a762006200726307017707ffffffffffff0b0a014c475a0003403b49070100620affff72620165021d770775770701006032010101010101044c475a0177070100600100ff010101010b0a014c475a0003403b490177070100010800ff65001c010472620165021d7707621e52ff690000000003152c450177070100020800ff0172620165021d7707621e52ff6900000000000000000177070100100700ff0101621b52005900000000000000fb010101637264007605065850a862006200726302017101631c8c00'
Exception <class 'sml2mqtt.errors.ObisIdForConfigurationMappingNotFoundError'>: ""
ERROR
/device_name/status: ERROR (QOS: 0, retain: False)'''
