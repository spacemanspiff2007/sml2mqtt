from binascii import a2b_hex

import pytest

from sml2mqtt.sml_device import SmlDevice


@pytest.mark.ignore_log_warnings()
async def test_device_analyze(no_mqtt, caplog, sml_data_1: bytes, arg_analyze, sml_frame_1_analyze):
    device = SmlDevice('device_name')
    device.frame_handler = device.analyze_frame

    # feed data in chunks
    chunk_size = 100
    for i in range(0, len(sml_data_1), chunk_size):
        device.on_source_data(a2b_hex(sml_data_1[i: i + chunk_size]))

    # This is what will be reported
    msg = "\n".join(x.msg for x in filter(lambda x: x.name == 'sml.mqtt.pub', caplog.records))

    assert '\n' + msg == """
/00000000000000000000/0100000009ff: 00000000000000000000 (QOS: 0, retain: False)
/00000000000000000000/0100010800ff: 450.09189911 (QOS: 0, retain: False)
/00000000000000000000/0100010801ff: 449.07489911 (QOS: 0, retain: False)
/00000000000000000000/0100010802ff: 1.0170000000000001 (QOS: 0, retain: False)
/00000000000000000000/0100020800ff: 2.198 (QOS: 0, retain: False)
/00000000000000000000/0100100700ff: 352.89 (QOS: 0, retain: False)
/00000000000000000000/0100240700ff: 82.26 (QOS: 0, retain: False)
/00000000000000000000/0100380700ff: 27.06 (QOS: 0, retain: False)
/00000000000000000000/01004c0700ff: 243.57 (QOS: 0, retain: False)
/00000000000000000000/status: OK (QOS: 0, retain: False)
/00000000000000000000/status: SHUTDOWN (QOS: 0, retain: False)"""

    msg = "\n".join(x.msg for x in filter(lambda x: x.name == 'sml.device_name', caplog.records))

    assert msg == sml_frame_1_analyze + '''
Found obis id 0100000009ff in the sml frame
No configuration found for 00000000000000000000
No filters found for 0100000009ff, creating default filters
No filters found for 0100010800ff, creating default filters
No filters found for 0100010801ff, creating default filters
No filters found for 0100010802ff, creating default filters
No filters found for 0100020800ff, creating default filters
No filters found for 0100100700ff, creating default filters
No filters found for 0100240700ff, creating default filters
No filters found for 0100380700ff, creating default filters
No filters found for 01004c0700ff, creating default filters
Skipped: 0100000009ff, 0100600100ff

<SmlValue>
  obis : 0100000009ff
  topic: /00000000000000000000/0100000009ff
  operations:
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100010800ff
  topic: /00000000000000000000/0100010800ff
  operations:
    - Factor: 0.001
    - ZeroMeterFilter
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100010801ff
  topic: /00000000000000000000/0100010801ff
  operations:
    - Factor: 0.001
    - ZeroMeterFilter
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100010802ff
  topic: /00000000000000000000/0100010802ff
  operations:
    - Factor: 0.001
    - ZeroMeterFilter
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100020800ff
  topic: /00000000000000000000/0100020800ff
  operations:
    - Factor: 0.001
    - ZeroMeterFilter
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100100700ff
  topic: /00000000000000000000/0100100700ff
  operations:
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100240700ff
  topic: /00000000000000000000/0100240700ff
  operations:
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 0100380700ff
  topic: /00000000000000000000/0100380700ff
  operations:
    - OnChangeFilter
    - RepublishFilter: 120s

<SmlValue>
  obis : 01004c0700ff
  topic: /00000000000000000000/01004c0700ff
  operations:
    - OnChangeFilter
    - RepublishFilter: 120s

'''
