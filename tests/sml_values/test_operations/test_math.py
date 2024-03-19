from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    RoundOperation, LimitValueOperation,

)
from tests.sml_values.test_operations.helper import check_operation_repr, check_description


def test_factor():
    o = FactorOperation(5)
    check_operation_repr(o, '5')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 25
    assert o.process_value(1.25, None) == 6.25
    assert o.process_value(-3, None) == -15


def test_offset():
    o = OffsetOperation(-5)
    check_operation_repr(o, '-5')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 0
    assert o.process_value(1.25, None) == -3.75
    assert o.process_value(-3, None) == -8


def test_round():
    o = RoundOperation(0)
    check_operation_repr(o, '0')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(1.25, None) == 1
    assert o.process_value(-3, None) == -3
    assert o.process_value(-3.65, None) == -4

    o = RoundOperation(1)
    check_operation_repr(o, '1')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(1.25, None) == 1.2
    assert o.process_value(-3, None) == -3
    assert o.process_value(-3.65, None) == -3.6


def test_limit_value():

    # ---------------------------------------------------------------------------------------------
    # Min
    o = LimitValueOperation(1, None, False)
    check_operation_repr(o, 'min=1 max=None ignore=False')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(1, None) == 1
    assert o.process_value(0.999, None) == 1

    o = LimitValueOperation(1, None, True)
    check_operation_repr(o, 'min=1 max=None ignore=True')

    assert o.process_value(None, None) is None
    assert o.process_value(1, None) == 1
    assert o.process_value(0.999, None) is None

    # ---------------------------------------------------------------------------------------------
    # Max
    o = LimitValueOperation(None, 5, False)
    check_operation_repr(o, 'min=None max=5 ignore=False')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(4.99, None) == 4.99
    assert o.process_value(5.01, None) == 5

    o = LimitValueOperation(None, 5, True)
    check_operation_repr(o, 'min=None max=5 ignore=True')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(4.99, None) == 4.99
    assert o.process_value(5.01, None) is None

    # ---------------------------------------------------------------------------------------------
    # Min Max
    o = LimitValueOperation(0, 5, False)
    check_operation_repr(o, 'min=0 max=5 ignore=False')

    assert o.process_value(None, None) is None
    assert o.process_value(-0.001, None) == 0
    assert o.process_value(0.001, None) == 0.001
    assert o.process_value(4.999, None) == 4.999
    assert o.process_value(5.001, None) == 5

    o = LimitValueOperation(0, 5, True)
    check_operation_repr(o, 'min=0 max=5 ignore=True')

    assert o.process_value(None, None) is None
    assert o.process_value(-0.001, None) is None
    assert o.process_value(0, None) == 0
    assert o.process_value(5, None) == 5
    assert o.process_value(5.001, None) is None


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
        RoundOperation(0),
        '- Round: integer'
    )

    check_description(
        RoundOperation(1),
        '- Round: 1'
    )

    # LimitValueOperation
    check_description(
        LimitValueOperation(1, None),
        ['- Limit value:', '    min: 1', '    ignore out of range: False']
    )
    check_description(
        LimitValueOperation(None, 7),
        ['- Limit value:', '    max: 7', '    ignore out of range: False']
    )
    check_description(
        LimitValueOperation(1, 7, True), [
            '- Limit value:',
            '    min: 1',
            '    max: 7',
            '    ignore out of range: True'
        ]
    )
