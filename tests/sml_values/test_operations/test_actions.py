from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.operations import RefreshActionOperation, ThrottleActionOperation
from sml2mqtt.sml_value.operations._helper import format_period


def test_format_period():
    assert format_period(30.2) == '30.2 seconds'
    assert format_period(30) == '30 seconds'
    assert format_period(60) == '1 minute'
    assert format_period(61) == '1 minute 1 second'
    assert format_period(121) == '2 minutes 1 second'
    assert format_period(3661) == '1 hour 1 minute 1 second'
    assert format_period(3722) == '1 hour 2 minutes 2 seconds'


def test_refresh_action(monotonic):
    f = RefreshActionOperation(30)
    check_operation_repr(f, '30s')
    check_description(f, '- Refresh Action: 30 seconds')

    assert f.process_value(1, None) == 1
    assert f.process_value(None, None) is None

    monotonic.add(5)
    assert f.process_value(2, None) == 2
    assert f.process_value(None, None) is None

    monotonic.add(29.99)
    assert f.process_value(None, None) is None

    monotonic.add(0.02)
    assert f.process_value(None, None) == 2


def test_throttle_action(monotonic):
    f = ThrottleActionOperation(30)
    check_operation_repr(f, '30s')
    check_description(f, '- Throttle Action: 30 seconds')

    assert f.process_value(None, None) is None
    assert f.process_value(1, None) == 1

    monotonic.set(29.99)
    assert f.process_value(1, None) is None
    monotonic.set(30)
    assert f.process_value(1, None) == 1

    monotonic.set(59.99)
    assert f.process_value(1, None) is None
    monotonic.set(60)
    assert f.process_value(1, None) == 1
