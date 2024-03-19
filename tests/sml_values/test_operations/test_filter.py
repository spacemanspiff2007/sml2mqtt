from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.operations import (
    AbsDeltaFilterOperation,
    HeartbeatFilterOperation,
    OnChangeFilterOperation,
    PercDeltaFilterOperation,
    SkipZeroMeterOperation,
)


def test_skip():
    f = SkipZeroMeterOperation()
    check_operation_repr(f)

    assert f.process_value(0, None) is None
    assert f.process_value(0.01, None) is None
    assert f.process_value(1, None) == 1
    assert f.process_value(1.1, None) == 1.1

    check_description(
        SkipZeroMeterOperation(),
        '- ZeroMeterFilter'
    )


def test_heartbeat(monotonic):
    f = HeartbeatFilterOperation(30)
    check_operation_repr(f, '30s')

    assert f.process_value(1, None) == 1

    monotonic.add(15)
    assert f.process_value(2, None) is None

    monotonic.add(14.99)
    assert f.process_value(3, None) is None

    monotonic.add(0.01)
    assert f.process_value(None, None) == 3
    assert f.process_value(2, None) is None

    monotonic.add(30.01)
    assert f.process_value(5, None) == 5
    assert f.process_value(5, None) is None

    check_description(
        HeartbeatFilterOperation(30),
        '- HeartbeatFilter: 30s'
    )


def test_diff_percent():
    f = PercDeltaFilterOperation(5)
    check_operation_repr(f, '5%')

    assert f.process_value(100, None) == 100
    assert f.process_value(104.999, None) is None
    assert f.process_value(95.001, None) is None

    assert f.process_value(105, None) == 105
    assert f.process_value(109.999, None) is None
    assert f.process_value(99.750001, None) is None
    assert f.process_value(99.75, None) == 99.75

    check_description(
        PercDeltaFilterOperation(5),
        '- DeltaFilter: 5%'
    )


def test_diff_abs():
    f = AbsDeltaFilterOperation(5)
    check_operation_repr(f, '5')

    assert f.process_value(10, None) == 10
    assert f.process_value(14.999, None) is None
    assert f.process_value(5.001, None) is None

    assert f.process_value(15, None) == 15
    assert f.process_value(10.0001, None) is None
    assert f.process_value(19.9999, None) is None
    assert f.process_value(10, None) == 10

    check_description(
        AbsDeltaFilterOperation(5),
        '- DeltaFilter: 5'
    )


def test_on_change():
    f = OnChangeFilterOperation()
    check_operation_repr(f)

    assert f.process_value(10, None) == 10
    assert f.process_value(10, None) is None
    assert f.process_value(11, None) == 11
    assert f.process_value(0, None) == 0

    check_description(
        OnChangeFilterOperation(),
        '- OnChangeFilter'
    )
