import logging

import pytest

from sml2mqtt.const import SmlFrameValues
from sml2mqtt.errors import (
    UnprocessedObisValuesReceivedError,
)
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.sml_value import SmlValue, SmlValues
from sml2mqtt.sml_value.operations import OnChangeFilterOperation
from sml_values.test_operations.helper import check_description


def test_values(sml_frame_1_values: SmlFrameValues, no_mqtt) -> None:
    mqtt = MqttObj(topic_fragment='test', qos=0, retain=False).update()

    v = SmlValues(logging.getLogger('test'))
    v.set_skipped('010060320101', '0100600100ff', '0100020800ff')

    v.add_value(
        SmlValue('0100010800ff', mqtt.create_child('energy')).add_operation(OnChangeFilterOperation())
    )
    v.add_value(
        SmlValue('0100100700ff', mqtt.create_child('power')).add_operation(OnChangeFilterOperation())
    )

    # The change filter prevents a republish
    for _ in range(10):
        v.process_frame(sml_frame_1_values)
        assert no_mqtt == [('test/energy', 253917.7, 0, False), ('test/power', 272, 0, False)]

    # test description
    check_description(v, [
        'Skipped: 0100020800ff, 0100600100ff, 010060320101',
        '',
        '<SmlValue>',
        '  obis : 0100010800ff',
        '  topic: test/energy',
        '  operations:',
        '    - On Change Filter',
        '',
        '<SmlValue>',
        '  obis : 0100100700ff',
        '  topic: test/power',
        '  operations:',
        '    - On Change Filter',
        '',
    ])


def get_log_messages(caplog, only_level: int | None = None) -> list[str]:
    msgs = []
    for rec_tuple in caplog.record_tuples:
        name, level, msg = rec_tuple
        assert name == 'test'
        if only_level is not None:
            assert level == only_level
            msgs.append(msg)
        else:
            assert level in (logging.ERROR, logging.WARNING, logging.INFO)
            msgs.append((level, msg))

    return msgs


@pytest.mark.ignore_log_warnings
@pytest.mark.ignore_log_errors
def test_too_much(sml_frame_1_values: SmlFrameValues, no_mqtt, caplog) -> None:
    v = SmlValues(logging.getLogger('test'))
    v.set_skipped('010060320101', '0100600100ff')

    v.add_value(
        SmlValue('0100010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )
    v.add_value(
        SmlValue('0100100700ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    with pytest.raises(UnprocessedObisValuesReceivedError) as e:
        v.process_frame(sml_frame_1_values)

    e.value.log_msg(logging.getLogger('test'))
    assert get_log_messages(caplog, only_level=logging.ERROR) == [
        'Unexpected obis id received!',
        '<SmlListEntry>',
        '  obis           : 0100020800ff (1-0:2.8.0*255)',
        '  status         : None',
        '  val_time       : None',
        '  unit           : 30',
        '  scaler         : -1',
        '  value          : 0',
        '  value_signature: None',
        '  -> 0.0Wh (Zählerstand Einspeisung Total)'
    ]


@pytest.mark.ignore_log_warnings
def test_missing(sml_frame_1_values: SmlFrameValues, no_mqtt, caplog) -> None:
    v = SmlValues(logging.getLogger('test'))
    v.set_skipped('010060320101', '0100600100ff', '0100020800ff', '0100010800ff', '0100100700ff')

    v.add_value(
        SmlValue('1100010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    v.process_frame(sml_frame_1_values)
    # second time logs nothing
    v.process_frame(sml_frame_1_values)
    assert get_log_messages(caplog, only_level=logging.WARNING) == [
        'Configured OBIS id missing in frame: 1100010800ff!'
    ]

    # Now two values are missing
    v.add_value(
        SmlValue('1200010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    # log should show all missing ids
    v.process_frame(sml_frame_1_values)
    # second call logs nothing
    v.process_frame(sml_frame_1_values)
    assert get_log_messages(caplog, only_level=logging.WARNING) == [
        'Configured OBIS id missing in frame: 1100010800ff!',
        'Configured OBIS ids missing in frame: 1100010800ff, 1200010800ff!'
    ]

    # now we receive the missing obis
    sml_frame_1_values.values['1100010800ff'] = sml_frame_1_values.values['0100010800ff']
    v.process_frame(sml_frame_1_values)
    v.process_frame(sml_frame_1_values)
    v.process_frame(sml_frame_1_values)
    assert get_log_messages(caplog) == [
        (logging.WARNING, 'Configured OBIS id missing in frame: 1100010800ff!'),
        (logging.WARNING, 'Configured OBIS ids missing in frame: 1100010800ff, 1200010800ff!'),
        (logging.INFO, 'OBIS id that was missing was received: 1100010800ff')
    ]
