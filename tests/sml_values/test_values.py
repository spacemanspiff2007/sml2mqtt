import logging

import pytest

from sml2mqtt.const import SmlFrameValues
from sml2mqtt.errors import (
    RequiredObisValueNotInFrameError,
    Sml2MqttExceptionWithLog,
    UnprocessedObisValuesReceivedError,
)
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.sml_value import SmlValue, SmlValues
from sml2mqtt.sml_value.operations import OnChangeFilterOperation


def test_values(sml_frame_values_1: SmlFrameValues, no_mqtt):
    mqtt = MqttObj(qos=0, retain=False)

    v = SmlValues()
    v.set_skipped('010060320101', '0100600100ff', '0100020800ff')

    v.add_value(
        SmlValue('0100010800ff', mqtt.create_child('energy')).add_operation(OnChangeFilterOperation())
    )
    v.add_value(
        SmlValue('0100100700ff', mqtt.create_child('power')).add_operation(OnChangeFilterOperation())
    )

    # The change filter prevents a republish
    for _ in range(10):
        v.process_frame(sml_frame_values_1)
        assert no_mqtt == [('/energy', 253917.7, 0, False), ('/power', 272, 0, False)]


def get_error_message(e: Sml2MqttExceptionWithLog, caplog) -> list[str]:
    e.log_msg(logging.getLogger('test'))

    msgs = []
    for rec_tuple in caplog.record_tuples:
        name, level, msg = rec_tuple
        assert name == 'test'
        assert level == logging.ERROR
        msgs.append(msg)

    return msgs


def test_too_much(sml_frame_values_1: SmlFrameValues, no_mqtt, caplog):
    v = SmlValues()
    v.set_skipped('010060320101', '0100600100ff')

    v.add_value(
        SmlValue('0100010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )
    v.add_value(
        SmlValue('0100100700ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    with pytest.raises(UnprocessedObisValuesReceivedError) as e:
        v.process_frame(sml_frame_values_1)

    assert get_error_message(e.value, caplog) == [
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


def test_missing(sml_frame_values_1: SmlFrameValues, no_mqtt, caplog):
    v = SmlValues()
    v.set_skipped('010060320101', '0100600100ff', '0100020800ff', '0100010800ff', '0100100700ff')

    v.add_value(
        SmlValue('1100010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    with pytest.raises(RequiredObisValueNotInFrameError) as e:
        v.process_frame(sml_frame_values_1)

    assert get_error_message(e.value, caplog) == ['Expected obis id missing in frame: 1100010800ff!']

    # Now two values are missing
    v.add_value(
        SmlValue('1200010800ff', MqttObj()).add_operation(OnChangeFilterOperation())
    )

    with pytest.raises(RequiredObisValueNotInFrameError) as e:
        v.process_frame(sml_frame_values_1)

    assert get_error_message(e.value, caplog) == [
        'Expected obis id missing in frame: 1100010800ff!',
        'Expected obis ids missing in frame: 1100010800ff, 1200010800ff!'
    ]
