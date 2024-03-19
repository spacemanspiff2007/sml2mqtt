from collections.abc import Generator
from datetime import datetime, timedelta
from datetime import time as dt_time
from typing import Final

from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


def get_now():
    return datetime.now()


class DateTimeFinder:
    def __init__(self):
        self.times: tuple[dt_time, ...] = ()
        self.dows: tuple[int, ...] = ()
        self.days: tuple[int, ...] = ()

    @property
    def condition_count(self) -> int:
        return len(self.times) + len(self.dows) + len(self.days)

    def add_time(self, time: dt_time):
        if not isinstance(time, dt_time):
            raise TypeError()
        self.times = (*self.times, time)
        return self

    def add_dow(self, dow: int):
        if not isinstance(dow, int):
            raise TypeError()
        if dow < 1 or dow > 7 or dow in self.dows:
            raise ValueError()
        self.dows = (*self.dows, dow)
        return self

    def add_day(self, day: int):
        if not isinstance(day, int):
            raise TypeError()
        if day < 1 or day > 31 or day in self.days:
            raise ValueError()
        self.days = (*self.days, day)
        return self

    def calc_next(self, now: datetime | None = None) -> datetime:
        if now is None:
            now = get_now()

        next_dt = now
        while True:
            date = next_dt.date()
            for time in self.times:
                if (new := datetime.combine(date, time)) > now:
                    return new

            while True:
                next_dt += timedelta(days=1)
                if (not self.dows and not self.days or
                        next_dt.isoweekday() in self.dows or
                        next_dt.day in self.days):
                    break


class VirtualMeterOperation(ValueOperationBase):
    def __init__(self, dt_finder: DateTimeFinder, start_now: bool = True):
        self.dt_finder: Final = dt_finder
        self.next_reset: datetime = get_now() if start_now else self.dt_finder.calc_next()
        self.last_value: float | None = None
        self.offset: float | None = None

        if start_now:
            self.process_value_backup = self.process_value
            self.process_value = self.process_value_start_now

    def process_value_start_now(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None
        self.last_value = value

        # restore original function
        name = 'process_value_backup'
        self.process_value = getattr(self, name)
        delattr(self, name)

        return self.process_value(value, info)

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if (now := get_now()) >= self.next_reset:
            self.next_reset = self.dt_finder.calc_next(now)
            self.offset = self.last_value

        self.last_value = value

        if (offset := self.offset) is None:
            return None

        return value - offset

    def __repr__(self):
        return (f'<VirtualMeter: next_reset={self.next_reset} offset={self.offset} '
                f'last_value={self.last_value} at 0x{id(self):x}>')

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Virtual meter:'
        yield f'{indent:s}    Offset: {self.offset}'
        yield f'{indent:s}    Next resets:'
        yield f'{indent:s}     - {self.next_reset}'

        next_dt = self.next_reset

        # for every condition we want to show two values
        samples = max(self.dt_finder.condition_count * 2 - 1, 2)
        for _ in range(samples):
            next_dt = self.dt_finder.calc_next(next_dt)
            yield f'{indent:s}     - {next_dt}'
