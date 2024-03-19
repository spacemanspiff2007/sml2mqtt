from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.base import SmlValueInfo
from sml2mqtt.sml_value.operations import RefreshActionOperation


def test_refresh_action(monotonic):
    f = RefreshActionOperation(30)
    check_operation_repr(f, '30s')

    assert f.process_value(1, None) == 1
    assert f.process_value(None, None) is None

    monotonic.add(5)
    assert f.process_value(2, None) == 2
    assert f.process_value(None, None) is None

    monotonic.add(29.99)
    assert f.process_value(None, None) is None

    monotonic.add(0.02)
    assert f.process_value(None, None) == 2

    check_description(
        RefreshActionOperation(30),
        '- RefreshAction: 30s'
    )
