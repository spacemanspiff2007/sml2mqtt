from typing import Any, Final, Literal
from unittest.mock import Mock

from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.base import ValueOperationBase
from sml2mqtt.sml_value.operations import OffsetOperation, OrOperation, SequenceOperation


def test_repr():
    check_operation_repr(OrOperation())
    check_operation_repr(SequenceOperation())


class MockOperationsGroup:
    def __init__(self, operation: ValueOperationBase):
        self.sentinel = object()
        self.operation: Final = operation
        self.mocks: list[Mock] = []

    def assert_called(self, *args: float | Literal['-']):
        for mock, arg in zip(self.mocks, args, strict=True):    # type: Mock, float | Literal['-']
            if arg == '-':
                mock.assert_not_called()
            else:
                mock.assert_called_once_with(arg, self.sentinel)

    def get_operation_mock(self, return_value: Any) -> Mock:
        m = Mock(spec_set=['process_value'])
        m.process_value = f = Mock(return_value=return_value)
        self.mocks.append(f)
        return m

    def process_value(self, value: float):
        return self.operation.process_value(value, self.sentinel)


def get_mock_group(cls: type[OrOperation | SequenceOperation], *return_values: Any) -> MockOperationsGroup:

    c = cls()
    m = MockOperationsGroup(c)
    for return_value in return_values:
        c.add_operation(m.get_operation_mock(return_value))
    return m


def test_or_no_exit():
    m = get_mock_group(OrOperation, None, None, None)
    assert m.process_value(1) is None
    m.assert_called(1, 1, 1)


def test_or_last_exit():
    m = get_mock_group(OrOperation, None, None, 5)
    assert m.process_value(1) == 5
    m.assert_called(1, 1, 1)


def test_or_first_exit():
    m = get_mock_group(OrOperation, 3, 99, 77)
    assert m.process_value(1) == 3
    m.assert_called(1, 1, 1)


def test_or_single():
    m = get_mock_group(OrOperation, None)
    assert m.process_value(1) is None
    m.assert_called(1)

    m = get_mock_group(OrOperation, 11)
    assert m.process_value(1) == 11
    m.assert_called(1)


def test_or_description():
    o = OrOperation()
    o.add_operation(OffsetOperation(3))

    check_description(
        o, [
            '- Or:',
            '  - Offset: 3',
        ]
    )

    o.add_operation(OffsetOperation(9))

    check_description(
        o, [
            '- Or:',
            '  - Offset: 3',
            '  - Offset: 9',
        ]
    )

    assert o.process_value(0, None) == 3
    assert o.process_value(None, None) is None


def test_seq_no_exit():
    m = get_mock_group(SequenceOperation, 1, 2, 3)
    assert m.process_value(0) == 3
    m.assert_called(0, 1, 2)


def test_seq_first_exit():
    m = get_mock_group(SequenceOperation, None, 2, None)
    assert m.process_value(1) is None
    m.assert_called(1, None, 2)


def test_seq_last_exit():
    m = get_mock_group(SequenceOperation, 1, 2, None)
    assert m.process_value(0) is None
    m.assert_called(0, 1, 2)


def test_seq_single():
    m = get_mock_group(SequenceOperation, None)
    assert m.process_value(1) is None
    m.assert_called(1)

    m = get_mock_group(SequenceOperation, 11)
    assert m.process_value(1) == 11
    m.assert_called(1)


def test_sequence_description():
    o = SequenceOperation()
    o.add_operation(OffsetOperation(3))

    check_description(
        o, [
            '- Sequence:',
            '  - Offset: 3',
        ]
    )

    o.add_operation(OffsetOperation(9))

    check_description(
        o, [
            '- Sequence:',
            '  - Offset: 3',
            '  - Offset: 9',
        ]
    )
