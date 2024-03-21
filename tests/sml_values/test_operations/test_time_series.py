import pytest

from sml2mqtt.const import SmlFrameValues, TimeSeries
from sml2mqtt.sml_value.base import SmlValueInfo
from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    RoundOperation, LimitValueOperation, MaxOfIntervalOperation, MinOfIntervalOperation, MeanOfIntervalOperation,

)

from tests.sml_values.test_operations.helper import check_operation_repr, check_description


def info(timestamp: int):
    return SmlValueInfo(None, SmlFrameValues.create(timestamp, []), 0)


def test_max():
    o = MaxOfIntervalOperation(TimeSeries(5), False)
    check_operation_repr(o, 'interval=5s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(5, info(0)) == 5
    assert o.process_value(3, info(3)) == 5
    assert o.process_value(2, info(8)) == 3
    assert o.process_value(1, info(13)) == 2
    assert o.process_value(1, info(14)) == 2

    o = MaxOfIntervalOperation(TimeSeries(5, wait_for_data=True), False)
    check_operation_repr(o, 'interval=5s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(5, info(0)) is None
    assert o.process_value(3, info(3)) is None
    assert o.process_value(2, info(8)) == 3
    assert o.process_value(1, info(13)) == 2
    assert o.process_value(1, info(14)) == 2

    o = MaxOfIntervalOperation(TimeSeries(5, wait_for_data=True), True)
    check_operation_repr(o, 'interval=5s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(5, info(0)) is None
    assert o.process_value(3, info(3)) is None
    assert o.process_value(2, info(8)) == 3
    assert o.process_value(2, info(10)) is None
    assert o.process_value(1, info(14)) is None
    assert o.process_value(1, info(15)) == 2

    check_description(
        o, [
            '- Max of interval:',
            '    Interval: 5s',
            '    Wait for data: True',
            '    Reset after value: True',
        ]
    )


def test_min():
    o = MinOfIntervalOperation(TimeSeries(5), False)
    check_operation_repr(o, 'interval=5s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(1, info(0)) == 1
    assert o.process_value(2, info(3)) == 1
    assert o.process_value(3, info(8)) == 2
    assert o.process_value(4, info(13)) == 3
    assert o.process_value(5, info(14)) == 3

    check_description(
        o, [
            '- Min of interval:',
            '    Interval: 5s',
            '    Wait for data: False',
            '    Reset after value: False',
        ]
    )


def test_mean():
    o = MeanOfIntervalOperation(TimeSeries(10), False)
    check_operation_repr(o, 'interval=10s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(1, info(0)) is None
    assert o.process_value(2, info(5)) == 1
    assert o.process_value(2, info(10)) == 1.5
    assert o.process_value(2, info(13)) == 1.8
    assert o.process_value(4, info(15)) == 2
    assert o.process_value(4, info(20)) == 3

    o = MeanOfIntervalOperation(TimeSeries(10, wait_for_data=True), False)
    check_operation_repr(o, 'interval=10s')

    assert o.process_value(None, info(0)) is None
    assert o.process_value(1, info(0)) is None
    assert o.process_value(2, info(5)) is None
    assert o.process_value(2, info(10)) == 1.5
    assert o.process_value(2, info(13)) == 1.8
    assert o.process_value(4, info(15)) == 2
    assert o.process_value(4, info(20)) == 3

    check_description(
        o, [
            '- Mean of interval:',
            '    Interval: 10s',
            '    Wait for data: True',
            '    Reset after value: False',
        ]
    )
