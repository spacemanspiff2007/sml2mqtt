from collections import deque
from datetime import timedelta
from time import monotonic
from typing import Final
from collections.abc import Generator
from typing import Final

from typing_extensions import override

from sml2mqtt.errors import RequiredObisValueNotInFrameError
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class TimeSeries:
    __slots__ = ('period', 'times', 'values')

    def __init__(self, period: int | float | timedelta):
        self.period: Final = period if isinstance(period, int | str) else period.total_seconds()
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

    def get_values(self) -> Generator[float, None, None]:
        yield from self.values

    def get_duration_values(self):
        ...


class MaxInInterval(ValueOperationBase):
    def __init__(self, period: int | float | timedelta):
        self.values = TimeSeries(period)

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        self.values.add_value(value, info.frame.timestamp)

        for op in self.operations:
            value = op.process_value(value, info)
        return value

    def __repr__(self):
        return f'<Sequence at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Sequence:'
        for o in self.operations:
            yield from o.describe(indent + '  ')
