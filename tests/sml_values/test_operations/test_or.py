from unittest.mock import Mock

from sml2mqtt.sml_value.operations import OrOperation
from tests.sml_values.test_operations.helper import check_operation_repr


def test_repr():
    o = OrOperation()
    check_operation_repr(o)


def test_skip_none():

    m1 = Mock()
    m1.process_value = f1 = Mock(return_value=None)

    m2 = Mock()
    m2.process_value = f2 = Mock(return_value=None)

    m3 = Mock()
    m3.process_value = f3 = Mock(return_value=None)

    o = OrOperation()
    o.add_operation(m1)
    o.add_operation(m2)
    o.add_operation(m3)

    def reset_mocks():
        for m in (f1, f2, f3):
            m.reset_mock()
            m.assert_not_called()

    # No value -> we return None
    reset_mocks()

    assert o.process_value(1, None) is None

    f1.assert_called_once_with(1, None)
    f2.assert_called_once_with(1, None)
    f3.assert_called_once_with(1, None)

    # Last value returns -> all get called
    reset_mocks()
    f3.return_value = 11

    assert o.process_value(1, None) == 11

    f1.assert_called_once_with(1, None)
    f2.assert_called_once_with(1, None)
    f3.assert_called_once_with(1, None)

    # Fast exist
    reset_mocks()
    f1.return_value = 11

    assert o.process_value(1, None) == 11

    f1.assert_called_once_with(1, None)
    f2.assert_not_called()
    f3.assert_not_called()


def test_single():

    m1 = Mock()
    m1.process_value = f1 = Mock(return_value=None)

    o = OrOperation()
    o.add_operation(m1)

    f1.assert_not_called()
    assert o.process_value(1.11, None) is None
    f1.assert_called_once_with(1.11, None)

    f1.reset_mock()
    f1.return_value = 11

    f1.assert_not_called()
    assert o.process_value(1.11, None) == 11
    f1.assert_called_once_with(1.11, None)
