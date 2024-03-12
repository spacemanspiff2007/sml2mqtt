from collections import deque
from time import monotonic
from typing import Final


class TimeSeries:
    __slots__ = ('period', 'times', 'values')

    def __init__(self, period: int | float):
        self.period: Final = period
        self.times: Final[deque[float]] = deque()
        self.values: Final[deque[float]] = deque()

    def add_value(self, value: int | float, timestamp: float):
        try:
            # we keep one element that's out of the interval
            while self.times[1] + self.period < monotonic():
                self.times.popleft()
                self.values.popleft()
        except IndexError:
            pass

        self.times.append(timestamp)
        self.values.append(value)
