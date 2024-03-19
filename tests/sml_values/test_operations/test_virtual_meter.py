import pytest

from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    RoundOperation, LimitValueOperation, VirtualMeterOperation, DateTimeFinder

)
from tests.sml_values.test_operations.helper import check_operation_repr, check_description
from datetime import datetime
from datetime import time
from sml2mqtt.sml_value.operations import virtual_meter as virtual_meter_module


class PatchedNow:
    def __init__(self):
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
                 microsecond: int | None = 0):
        self.kwargs = {
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute, 'second': second, 'microsecond': microsecond
        }

    def create(self, *args, **kwargs):

        call = {}
        pos = 0
        for name, value in self.kwargs.items():
            value = kwargs.get(name, value)
            if value is None:
                if pos < len(args):
                    value = args[pos]
                    pos += 1

            call[name] = value

        assert len(args) == pos

        return datetime(**call)


@pytest.fixture()
def now(monkeypatch):
    p = PatchedNow()
    monkeypatch.setattr(virtual_meter_module, 'get_now', p)
    return p


def test_finder_1(now):
    f = DateTimeFinder()
    f.add_time(time(2))

    dt_set = DateTimeFactory(hour=1, minute=30)
    dt_next = DateTimeFactory(hour=2, minute=0)

    for i in range(1, 31):
        now.set(dt_set.create(i))
        assert f.calc_next() == dt_next.create(i)


def test_start_now(now):
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1, microsecond=1))

    o = VirtualMeterOperation(f, start_now=True)

    assert o.process_value(None, None) is None
    assert o.process_value(33, None) == 0
    assert o.process_value(34, None) == 1


def test_start_normal(now):
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


def test_description(now):
    f = DateTimeFinder()
    f.add_time(time(2))

    dt = DateTimeFactory(hour=1, minute=30)
    now.set(dt.create(1))

    o = VirtualMeterOperation(f, start_now=True)
    now.set(dt.create(1))

    assert o.process_value(1, None) == 0

    check_description(
        o, [
            '- Virtual meter:',
            '    Offset: 1',
            '    Next resets:',
            '     - 2001-01-01 02:00:00',
            '     - 2001-01-02 02:00:00',
            '     - 2001-01-03 02:00:00',
        ]
    )
