from tests.sml_values.test_operations.helper import check_operation_repr

from sml2mqtt.sml_value.base import SmlValueInfo
from sml2mqtt.sml_value.operations import (
    AbsDiffFilterOperation,
    HeartbeatFilterOperation,
    OnChangeFilterOperation,
    PercDiffFilterOperation,
    SkipZeroMeterOperation,
)


def test_skip():
    f = SkipZeroMeterOperation()
    check_operation_repr(f)

    assert f.process_value(0, None) is None
    assert f.process_value(0.01, None) is None
    assert f.process_value(1, None) == 1
    assert f.process_value(1.1, None) == 1.1


def test_heartbeat(monotonic):
    f = HeartbeatFilterOperation(30)
    check_operation_repr(f, '30s')

    info = SmlValueInfo(None, None, 0)

    assert f.process_value(1, info) is None

    monotonic.add(29.99)
    assert f.process_value(1, info) is None

    monotonic.add(0.01)
    assert f.process_value(1, info) == 1


def test_diff_percent():
    f = PercDiffFilterOperation(5)
    check_operation_repr(f, '5%')

    assert f.process_value(100, None) == 100
    assert f.process_value(104.999, None) is None
    assert f.process_value(95.001, None) is None

    assert f.process_value(105, None) == 105
    assert f.process_value(109.999, None) is None
    assert f.process_value(99.750001, None) is None
    assert f.process_value(99.75, None) == 99.75


def test_diff_abs():
    f = AbsDiffFilterOperation(5)
    check_operation_repr(f, '5')

    assert f.process_value(10, None) == 10
    assert f.process_value(14.999, None) is None
    assert f.process_value(5.001, None) is None

    assert f.process_value(15, None) == 15
    assert f.process_value(10.0001, None) is None
    assert f.process_value(19.9999, None) is None
    assert f.process_value(10, None) == 10


def test_on_change():
    f = OnChangeFilterOperation()
    check_operation_repr(f)

    assert f.process_value(10, None) == 10
    assert f.process_value(10, None) is None
    assert f.process_value(11, None) == 11
    assert f.process_value(0, None) == 0
