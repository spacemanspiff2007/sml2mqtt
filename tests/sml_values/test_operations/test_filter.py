from tests.sml_values.test_operations.helper import check_description, check_operation_repr

from sml2mqtt.sml_value.operations import (
    DeltaFilterOperation,
    OnChangeFilterOperation,
    RangeFilterOperation,
    SkipZeroMeterOperation,
    ThrottleFilterOperation,
)


def test_skip() -> None:
    f = SkipZeroMeterOperation()
    check_operation_repr(f)

    assert f.process_value(0, None) is None
    assert f.process_value(0.01, None) is None
    assert f.process_value(1, None) == 1
    assert f.process_value(1.1, None) == 1.1

    check_description(
        SkipZeroMeterOperation(),
        '- Zero Meter Filter'
    )


def test_delta() -> None:
    f = DeltaFilterOperation(min_value=5)
    check_operation_repr(f, 'min=5 min_percent=None')
    check_description(f, ['- Delta Filter:', '    Min  : 5'])

    assert f.process_value(10, None) == 10
    assert f.process_value(14.999, None) is None
    assert f.process_value(5.001, None) is None

    assert f.process_value(15, None) == 15
    assert f.process_value(10.0001, None) is None
    assert f.process_value(19.9999, None) is None
    assert f.process_value(10, None) == 10

    f = DeltaFilterOperation(min_percent=5)
    check_operation_repr(f, 'min=None min_percent=5')
    check_description(f, ['- Delta Filter:', '    Min %: 5'])

    assert f.process_value(0, None) == 0
    assert f.process_value(0.049, None) == 0.049

    assert f.process_value(100, None) == 100
    assert f.process_value(104.999, None) is None
    assert f.process_value(95.001, None) is None

    assert f.process_value(105, None) == 105
    assert f.process_value(109.999, None) is None
    assert f.process_value(99.750001, None) is None
    assert f.process_value(99.75, None) == 99.75

    f = DeltaFilterOperation(min_value=5, min_percent=10)
    check_operation_repr(f, 'min=5 min_percent=10')
    check_description(f, ['- Delta Filter:', '    Min  : 5', '    Min %: 10'])

    assert f.process_value(100, None) == 100
    assert f.process_value(109.99, None) is None
    assert f.process_value(110, None) == 110

    assert f.process_value(10, None) == 10
    assert f.process_value(14.99, None) is None
    assert f.process_value(15, None) == 15


def test_on_change() -> None:
    f = OnChangeFilterOperation()
    check_operation_repr(f)

    assert f.process_value(10, None) == 10
    assert f.process_value(10, None) is None
    assert f.process_value(11, None) == 11
    assert f.process_value(0, None) == 0

    check_description(
        OnChangeFilterOperation(),
        '- On Change Filter'
    )


def test_range() -> None:

    # ---------------------------------------------------------------------------------------------
    # Min
    o = RangeFilterOperation(1, None, True)
    check_operation_repr(o, 'min=1 max=None limit_values=True')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(1, None) == 1
    assert o.process_value(0.999, None) == 1

    o = RangeFilterOperation(1, None, False)
    check_operation_repr(o, 'min=1 max=None limit_values=False')

    assert o.process_value(None, None) is None
    assert o.process_value(1, None) == 1
    assert o.process_value(0.999, None) is None

    # ---------------------------------------------------------------------------------------------
    # Max
    o = RangeFilterOperation(None, 5, True)
    check_operation_repr(o, 'min=None max=5 limit_values=True')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(4.99, None) == 4.99
    assert o.process_value(5.01, None) == 5

    o = RangeFilterOperation(None, 5, False)
    check_operation_repr(o, 'min=None max=5 limit_values=False')

    assert o.process_value(None, None) is None
    assert o.process_value(5, None) == 5
    assert o.process_value(4.99, None) == 4.99
    assert o.process_value(5.01, None) is None

    # ---------------------------------------------------------------------------------------------
    # Min Max
    o = RangeFilterOperation(0, 5, True)
    check_operation_repr(o, 'min=0 max=5 limit_values=True')

    assert o.process_value(None, None) is None
    assert o.process_value(-0.001, None) == 0
    assert o.process_value(0.001, None) == 0.001
    assert o.process_value(4.999, None) == 4.999
    assert o.process_value(5.001, None) == 5

    o = RangeFilterOperation(0, 5, False)
    check_operation_repr(o, 'min=0 max=5 limit_values=False')

    assert o.process_value(None, None) is None
    assert o.process_value(-0.001, None) is None
    assert o.process_value(0, None) == 0
    assert o.process_value(5, None) == 5
    assert o.process_value(5.001, None) is None

    # LimitValueFilter
    check_description(
        RangeFilterOperation(1, None, False),
        ['- Range Filter:', '    min: 1', '    limit to min/max: False']
    )
    check_description(
        RangeFilterOperation(None, 7, False),
        ['- Range Filter:', '    max: 7', '    limit to min/max: False']
    )
    check_description(
        RangeFilterOperation(1, 7, True), [
            '- Range Filter:',
            '    min: 1',
            '    max: 7',
            '    limit to min/max: True'
        ]
    )


def test_throttle_filter(monotonic) -> None:
    f = ThrottleFilterOperation(30)
    check_operation_repr(f, '30s')
    check_description(f, '- Throttle Filter: 30 seconds')

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
