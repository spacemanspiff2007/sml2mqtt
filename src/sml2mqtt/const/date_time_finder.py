from datetime import datetime, timedelta
from datetime import time as dt_time


def get_now():
    return datetime.now()


class DateTimeFinder:
    def __init__(self) -> None:
        self.times: tuple[dt_time, ...] = ()
        self.dows: tuple[int, ...] = ()
        self.days: tuple[int, ...] = ()

        self.enabled: bool = False

    @property
    def condition_count(self) -> int:
        return len(self.times) + len(self.dows) + len(self.days)

    def add_time(self, time: dt_time):
        if not isinstance(time, dt_time):
            raise TypeError()
        self.times = (*self.times, time)
        self.enabled = True
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

    def get_first_reset(self, start_now: bool):
        return get_now() if start_now or not self.enabled else self.calc_next()

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
                if not self.dows and not self.days or next_dt.isoweekday() in self.dows or next_dt.day in self.days:
                    break
