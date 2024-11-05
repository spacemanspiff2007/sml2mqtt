from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.operations import HeartbeatActionOperation, RefreshActionOperation
from sml2mqtt.sml_value.operations._helper import format_period


def test_format_period() -> None:
    assert format_period(30.2) == '30.2 seconds'
    assert format_period(30) == '30 seconds'
    assert format_period(60) == '1 minute'
    assert format_period(61) == '1 minute 1 second'
    assert format_period(121) == '2 minutes 1 second'
    assert format_period(3661) == '1 hour 1 minute 1 second'
    assert format_period(3722) == '1 hour 2 minutes 2 seconds'


def test_refresh_action(monotonic) -> None:
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


def test_heartbeat_action(monotonic) -> None:
    f = HeartbeatActionOperation(30)
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
        HeartbeatActionOperation(30),
        '- Heartbeat Action: 30 seconds'
    )
