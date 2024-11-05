from collections import deque
from collections.abc import Sequence
from datetime import timedelta
from typing import Final, TypeAlias


DurationType: TypeAlias = timedelta | float | int


def get_duration(obj: DurationType) -> int | float:
    if isinstance(obj, timedelta):
        return int(obj.total_seconds()) if not obj.microseconds else obj.total_seconds()
    if not isinstance(obj, (int, float)):
        raise TypeError()
    return obj


class TimeSeries:
    __slots__ = ('period', 'times', 'values', 'is_full', 'wait_for_data')

    def __init__(self, period: DurationType, wait_for_data: bool = False) -> None:
        self.wait_for_data: Final = wait_for_data
        self.period: Final = get_duration(period)
        self.times: Final[deque[float]] = deque()
        self.values: Final[deque[float]] = deque()

        self.is_full: bool = False

    def clear(self) -> None:
        self.is_full = False
        self.times.clear()
        self.values.clear()

    def add_value(self, value: int | float | None, timestamp: float) -> None:
        start = timestamp - self.period

        if value is not None:
            self.times.append(timestamp)
            self.values.append(value)

        if not self.is_full and self.times and self.times[0] <= start:
            self.is_full = True

        try:
            while self.times[1] <= start:
                self.times.popleft()
                self.values.popleft()
        except IndexError:
            pass

    def get_values(self) -> Sequence[float] | None:
        if not self.values or self.wait_for_data and not self.is_full:
            return None
        return tuple(self.values)

    def get_value_duration(self, timestamp: float) -> Sequence[tuple[float, float]] | None:
        if not self.values or self.wait_for_data and not self.is_full:
            return None

        start_of_interval = timestamp - self.period

        start = self.times[0]
        if start <= start_of_interval:
            start = start_of_interval

        stop = timestamp
        value = self.values[0]

        ret = []
        for i in range(1, len(self.values)):
            stop = self.times[i]
            ret.append((value, stop - start))
            start = stop
            value = self.values[i]

        ret.append((value, stop - start))
        return ret
