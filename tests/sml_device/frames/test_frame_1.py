
import pytest

from sml2mqtt import CONFIG
from sml2mqtt.config.device import SmlDeviceConfig
from sml2mqtt.sml_device import SmlDevice


@pytest.mark.ignore_log_errors()
async def test_frame_no_match_obis_id(no_mqtt, caplog, monkeypatch, sml_frame_1, arg_analyze, sml_frame_1_analyze) -> None:
    device = SmlDevice('device_name')
    device.frame_handler = device.analyze_frame

    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100000009ff', '01006001ffff'])

    device.on_source_data(None)

    msg = '\n'.join(x.msg for x in caplog.records)

    assert msg.removeprefix(sml_frame_1_analyze) == '''
Found none of the following obis ids in the sml frame: 0100000009ff, 01006001ffff
Received Frame
 -> b'760500531efa620062007263010176010105001bb4fe0b0a0149534b0005020de272620165001bb32e620163a71400760500531efb620062007263070177010b0a0149534b0005020de2070100620affff72620165001bb32e757707010060320101010101010449534b0177070100600100ff010101010b0a0149534b0005020de20177070100010800ff65001c010401621e52ff650026bea90177070100020800ff0101621e52ff62000177070100100700ff0101621b52005301100101016350ba00760500531efc6200620072630201710163ba1900'
Exception <class 'sml2mqtt.errors.ObisIdForConfigurationMappingNotFoundError'>: ""
ERROR
device_name/status: ERROR (QOS: 0, retain: False)'''


@pytest.mark.ignore_log_warnings()
async def test_frame_no_config(no_mqtt, caplog, monkeypatch, sml_frame_1, arg_analyze, sml_frame_1_analyze) -> None:
    device = SmlDevice('device_name')
    device.frame_handler = device.analyze_frame

    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100600100ff'])

    device.on_source_data(None)

    msg = '\n'.join(x.msg for x in caplog.records)

    assert msg.removeprefix(sml_frame_1_analyze) == '''
Found obis id 0100600100ff in the sml frame
No device found for 0a0149534b0005020de2
No filters found for 010060320101, creating default filters
No filters found for 0100600100ff, creating default filters
No filters found for 0100010800ff, creating default filters
No filters found for 0100020800ff, creating default filters
No filters found for 0100100700ff, creating default filters
Skipped: 0100600100ff

<SmlValue>
  obis : 010060320101
  topic: 0a0149534b0005020de2/010060320101
  operations:
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100600100ff
  topic: 0a0149534b0005020de2/0100600100ff
  operations:
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100010800ff
  topic: 0a0149534b0005020de2/0100010800ff
  operations:
    - Zero Meter Filter
    - Factor: 0.001
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100020800ff
  topic: 0a0149534b0005020de2/0100020800ff
  operations:
    - Zero Meter Filter
    - Factor: 0.001
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100100700ff
  topic: 0a0149534b0005020de2/0100100700ff
  operations:
    - On Change Filter
    - Refresh Action: 2 minutes

0a0149534b0005020de2/010060320101: ISK (QOS: 0, retain: False)
0a0149534b0005020de2/0100600100ff: 0a0149534b0005020de2 (QOS: 0, retain: False)
0a0149534b0005020de2/0100010800ff: 253.91770000000002 (QOS: 0, retain: False)
0a0149534b0005020de2/0100100700ff: 272 (QOS: 0, retain: False)
OK
0a0149534b0005020de2/status: OK (QOS: 0, retain: False)

SHUTDOWN
0a0149534b0005020de2/status: SHUTDOWN (QOS: 0, retain: False)'''


async def test_frame_with_config(no_mqtt, caplog, monkeypatch, sml_frame_1, arg_analyze, sml_frame_1_analyze) -> None:
    device = SmlDevice('device_name')
    device.frame_handler = device.analyze_frame

    monkeypatch.setattr(CONFIG.general, 'device_id_obis', ['0100600100ff'])
    monkeypatch.setitem(CONFIG.devices, '0a0149534b0005020de2', SmlDeviceConfig(
        skip=['010060320101']
    ))

    device.on_source_data(None)

    msg = '\n'.join(x.msg for x in caplog.records)

    print(msg)

    assert msg.removeprefix(sml_frame_1_analyze) == '''
Found obis id 0100600100ff in the sml frame
Device found for 0a0149534b0005020de2
No filters found for 0100010800ff, creating default filters
No filters found for 0100020800ff, creating default filters
No filters found for 0100100700ff, creating default filters
Skipped: 0100600100ff, 010060320101

<SmlValue>
  obis : 0100010800ff
  topic: 0a0149534b0005020de2/0100010800ff
  operations:
    - Zero Meter Filter
    - Factor: 0.001
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100020800ff
  topic: 0a0149534b0005020de2/0100020800ff
  operations:
    - Zero Meter Filter
    - Factor: 0.001
    - On Change Filter
    - Refresh Action: 2 minutes

<SmlValue>
  obis : 0100100700ff
  topic: 0a0149534b0005020de2/0100100700ff
  operations:
    - On Change Filter
    - Refresh Action: 2 minutes

0a0149534b0005020de2/0100010800ff: 253.91770000000002 (QOS: 0, retain: False)
0a0149534b0005020de2/0100100700ff: 272 (QOS: 0, retain: False)
OK
0a0149534b0005020de2/status: OK (QOS: 0, retain: False)

SHUTDOWN
0a0149534b0005020de2/status: SHUTDOWN (QOS: 0, retain: False)'''
