from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    RoundOperation,
)
from tests.sml_values.test_operations.helper import check_operation_repr, check_description


def test_factor():
    o = FactorOperation(5)
    check_operation_repr(o, '5')

    assert o.process_value(5, None) == 25
    assert o.process_value(1.25, None) == 6.25
    assert o.process_value(-3, None) == -15


def test_offset():
    o = OffsetOperation(-5)
    check_operation_repr(o, '-5')

    assert o.process_value(5, None) == 0
    assert o.process_value(1.25, None) == -3.75
    assert o.process_value(-3, None) == -8


def test_round():
    o = RoundOperation()
    check_operation_repr(o, '0')
    o = RoundOperation(0)
    check_operation_repr(o, '0')

    assert o.process_value(5, None) == 5
    assert o.process_value(1.25, None) == 1
    assert o.process_value(-3, None) == -3
    assert o.process_value(-3.65, None) == -4

    o = RoundOperation(1)
    check_operation_repr(o, '1')

    assert o.process_value(5, None) == 5
    assert o.process_value(1.25, None) == 1.2
    assert o.process_value(-3, None) == -3
    assert o.process_value(-3.65, None) == -3.6


def test_description():
    check_description(
        FactorOperation(-5),
        '- Factor: -5'
    )

    check_description(
        FactorOperation(3.14),
        '- Factor: 3.14'
    )

    check_description(
        OffsetOperation(-5),
        '- Offset: -5'
    )

    check_description(
        OffsetOperation(3.14),
        '- Offset: 3.14'
    )

    check_description(
        RoundOperation(),
        '- Round: integer'
    )

    check_description(
        RoundOperation(1),
        '- Round: 1'
    )
