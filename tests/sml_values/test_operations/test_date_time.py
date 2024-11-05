from datetime import datetime, time

import pytest
from tests.sml_values.test_operations.helper import check_description

from sml2mqtt.const import date_time_finder as date_time_finder_module
from sml2mqtt.sml_value.operations import DateTimeFinder, MaxValueOperation, MinValueOperation, VirtualMeterOperation
from sml2mqtt.sml_value.operations import date_time as virtual_meter_module


class PatchedNow:
    def __init__(self) -> None:
        self.ret = None

    def set(self, dt: datetime):
        self.ret = dt
        return self.ret

    def __call__(self):
        assert self.ret
        return self.ret


class DateTimeFactory:
    def __init__(self, year: int | None = 2001, month: int | None = 1, day: int | None = None,
                 hour: int | None = None, minute: int | None = None, second: int | None = 0,
                 microsecond: int | None = 0) -> None:
        self.kwargs = {
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute, 'second': second, 'microsecond': microsecond
        }

    def create(self, *args, **kwargs):

        call = {}
        pos = 0
        for name, value in self.kwargs.items():
            value = kwargs.get(name, value)
            if value is None and pos < len(args):
                value = args[pos]
                pos += 1

            call[name] = value

        assert len(args) == pos

        return datetime(**call)


@pytest.fixture
def now(monkeypatch):
    p = PatchedNow()
    monkeypatch.setattr(virtual_meter_module, 'get_now', p)
    monkeypatch.setattr(date_time_finder_module, 'get_now', p)
    return p


def test_finder_1(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt_set = DateTimeFactory(hour=1, minute=30)
    dt_next = DateTimeFactory(hour=2, minute=0)

    for i in range(1, 31):
        now.set(dt_set.create(i))
        assert f.calc_next() == dt_next.create(i)


def test_finder_dow(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))
    f.add_dow(1)

    dt_set = DateTimeFactory(hour=1, minute=30)
    dt_next = DateTimeFactory(hour=2, minute=0)

    for i in range(1, 30, 7):
        now.set(dt_set.create(i))
        assert f.calc_next() == dt_next.create(i)


def test_finder_day(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))
    f.add_day(15)
    f.add_day(31)

    dt_set = DateTimeFactory(hour=1, minute=30)
    dt_next = DateTimeFactory(hour=2, minute=0)

    now.set(dt_set.create(15))
    assert f.calc_next() == dt_next.create(15)

    now.set(dt_set.create(31))
    assert f.calc_next() == dt_next.create(31)

    now.set(dt_set.create(15, month=2))
    assert f.calc_next() == dt_next.create(15, month=2)

    now.set(dt_set.create(15, month=3))
    assert f.calc_next() == dt_next.create(15, month=3)


def test_virtual_meter_start_now(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1, microsecond=1))

    o = VirtualMeterOperation(f, start_now=True)

    assert o.process_value(None, None) is None
    assert o.process_value(33, None) == 0
    assert o.process_value(34, None) == 1


def test_virtual_meter_start_normal(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1))

    o = VirtualMeterOperation(f, start_now=False)
    now.set(dt.create(1))

    assert o.process_value(None, None) is None
    assert o.process_value(33, None) is None
    assert o.process_value(34, None) is None

    now.set(dt.create(1, hour=2, minute=0, second=1))
    assert o.process_value(35, None) == 1


def test_virtual_meter_description(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1))

    o = VirtualMeterOperation(f, start_now=True)
    now.set(dt.create(1))

    assert o.process_value(1, None) == 0

    check_description(
        o, [
            '- Virtual Meter:',
            '    Offset: 1',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )


def test_virtual_meter_start_now_no_times(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1, microsecond=1))

    o = VirtualMeterOperation(f, start_now=True)

    assert o.process_value(None, None) is None
    assert o.process_value(33, None) == 0
    assert o.process_value(34, None) == 1


def test_virtual_meter_start_normal_no_times(now) -> None:
    f = DateTimeFinder()

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1))

    o = VirtualMeterOperation(f, start_now=False)
    now.set(dt.create(1))

    assert o.process_value(None, None) is None
    assert o.process_value(33, None) == 0
    assert o.process_value(34, None) == 1


def test_virtual_meter_description_no_times(now) -> None:
    f = DateTimeFinder()

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1))

    o = VirtualMeterOperation(f, start_now=True)
    now.set(dt.create(1))

    assert o.process_value(1, None) == 0

    check_description(
        o, [
            '- Virtual Meter:',
            '    Offset: 1',
            '    No resets',
        ]
    )


def test_max_start_now(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1, microsecond=1))

    o = MaxValueOperation(f, start_now=True)

    assert o.process_value(None, None) is None
    assert o.process_value(50, None) == 50
    assert o.process_value(33, None) is None
    assert o.process_value(50, None) is None
    assert o.process_value(51, None) == 51
    assert o.process_value(50, None) is None


def test_max_start_normal(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(day=1, hour=1, minute=0)
    now.set(dt.create(microsecond=1))

    o = MaxValueOperation(f, start_now=False)

    assert o.process_value(None, None) is None
    assert o.process_value(9999, None) is None

    now.set(dt.create(hour=2))

    assert o.process_value(None, None) is None
    assert o.process_value(50, None) == 50
    assert o.process_value(33, None) is None
    assert o.process_value(50, None) is None
    assert o.process_value(51, None) == 51
    assert o.process_value(50, None) is None


def test_max_description(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(day=1, hour=1, minute=0)
    now.set(dt.create(microsecond=1))

    o = MaxValueOperation(f, start_now=True)
    assert o.process_value(1, None) == 1

    check_description(
        o, [
            '- Max Value:',
            '    max: 1',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )

    o = MaxValueOperation(f, start_now=False)
    assert o.process_value(1, None) is None

    check_description(
        o, [
            '- Max Value:',
            '    max: None',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )

    now.set(datetime(2001, 1, 1, 2, 0, 1))
    check_description(
        o, [
            '- Max Value:',
            '    max: None',
            '    Next resets:',
            '     - now',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )


def test_min_start_now(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1, microsecond=1))

    o = MinValueOperation(f, start_now=True)

    assert o.process_value(None, None) is None
    assert o.process_value(50, None) == 50
    assert o.process_value(55, None) is None
    assert o.process_value(50, None) is None
    assert o.process_value(49, None) == 49
    assert o.process_value(49, None) is None


def test_min_start_normal(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(day=1, hour=1, minute=0)
    now.set(dt.create(microsecond=1))

    o = MinValueOperation(f, start_now=False)

    assert o.process_value(None, None) is None
    assert o.process_value(-9999, None) is None

    now.set(dt.create(hour=2))

    assert o.process_value(None, None) is None
    assert o.process_value(50, None) == 50
    assert o.process_value(55, None) is None
    assert o.process_value(50, None) is None
    assert o.process_value(49, None) == 49
    assert o.process_value(49, None) is None


def test_min_description(now) -> None:
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(day=1, hour=1, minute=0)
    now.set(dt.create(microsecond=1))

    o = MinValueOperation(f, start_now=True)
    assert o.process_value(1, None) == 1

    check_description(
        o, [
            '- Min Value:',
            '    min: 1',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )

    o = MinValueOperation(f, start_now=False)
    assert o.process_value(1, None) is None

    check_description(
        o, [
            '- Min Value:',
            '    min: None',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )
