from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.base import ValueOperationBase
from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    RoundOperation,
    RoundToMultipleOperation,
)


def check_values(o: ValueOperationBase, *values: tuple[float, float]) -> None:
    assert o.process_value(None, None) is None

    for _in, _out in values:
        _res = o.process_value(_in, None)
        assert _res == _out, f'in: {_in} out: {_res} expected: {_out}'
        assert isinstance(_res, type(_out))


def test_factor() -> None:
    o = FactorOperation(5)
    check_operation_repr(o, '5')

    check_values(o, (5, 25), (1.25, 6.25), (-3, -15))


def test_offset() -> None:
    o = OffsetOperation(-5)
    check_operation_repr(o, '-5')

    check_values(o, (5, 0), (1.25, -3.75), (-3, -8))


def test_round() -> None:
    o = RoundOperation(0)
    check_operation_repr(o, '0')
    check_values(o, (5, 5), (1.25, 1), (-3, -3), (-3.65, -4))

    o = RoundOperation(1)
    check_operation_repr(o, '1')
    check_values(o, (5, 5), (1.25, 1.2), (-3, -3), (-3.65, -3.6))

    o = RoundOperation(-1)
    check_operation_repr(o, '-1')
    check_values(o, (5, 0), (6, 10), (-5, 0), (-6, -10))


def test_round_to_value() -> None:
    o = RoundToMultipleOperation(20, 'up')
    check_operation_repr(o, 'value=20 round=up')
    check_values(
        o, (0, 0), (0.0001, 20), (20, 20), (39.999999, 40), (40, 40), (40.000001, 60), (-20, -20), (-20.000001, -20))

    o = RoundToMultipleOperation(20, 'down')
    check_operation_repr(o, 'value=20 round=down')
    check_values(
        o, (0, 0), (0.0001, 0), (20, 20), (39.999999, 20), (40, 40), (40.000001, 40), (-20, -20), (-20.000001, -40))

    o = RoundToMultipleOperation(20, 'nearest')
    check_operation_repr(o, 'value=20 round=nearest')
    check_values(
        o, (0, 0), (9.9999, 0), (10, 20), (29.999999, 20), (30, 40), (40.000001, 40), (-20, -20),
        (-30, -20), (-30.1, -40)
    )


def test_description() -> None:
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

    for mode in 'up', 'down', 'nearest':
        check_description(
            RoundToMultipleOperation(50, mode),
            ['- Round To Multiple:', '      value: 50', f'      round: {mode:s}']
        )
