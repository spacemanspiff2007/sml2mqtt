from collections.abc import Generator, Sequence
from typing import Final

from typing_extensions import override

from sml2mqtt.const import TimeSeries
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase
from sml2mqtt.sml_value.operations._helper import format_period


class TimeSeriesOperationBaseBase(ValueOperationBase):
    def __init__(self, time_series: TimeSeries, reset_after_value: bool) -> None:
        self.time_series: Final = time_series
        self.reset_after_value: Final = reset_after_value

        # Makes only sense in combination
        if reset_after_value and not time_series.wait_for_data:
            raise ValueError()

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}    Interval: {format_period(self.time_series.period)}'
        yield f'{indent:s}    Wait for data: {self.time_series.wait_for_data}'
        yield f'{indent:s}    Reset after value: {self.reset_after_value}'


class TimeSeriesOperationBase(TimeSeriesOperationBaseBase):
    def on_values(self, obj: Sequence[float]) -> float | None:
        raise NotImplementedError()

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:

        ts = info.frame.timestamp
        self.time_series.add_value(value, ts)

        if (values := self.time_series.get_values()) is None:
            return None

        if self.reset_after_value:
            self.time_series.clear()
        return self.on_values(values)


class TimeDurationSeriesOperationBase(TimeSeriesOperationBaseBase):
    def on_values(self, obj: Sequence[tuple[float, float]]) -> float | None:
        raise NotImplementedError()

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:

        ts = info.frame.timestamp
        self.time_series.add_value(value, ts)

        if (values := self.time_series.get_value_duration(ts)) is None:
            return None

        if self.reset_after_value:
            self.time_series.clear()
        return self.on_values(values)


class MaxOfIntervalOperation(TimeSeriesOperationBase):

    @override
    def on_values(self, obj: Sequence[float]) -> float | None:
        return max(obj)

    def __repr__(self) -> str:
        return f'<MaxOfInterval: interval={self.time_series.period}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Max Of Interval:'
        yield from super().describe(indent)


class MinOfIntervalOperation(TimeSeriesOperationBase):

    @override
    def on_values(self, obj: Sequence[float]) -> float | None:
        return min(obj)

    def __repr__(self) -> str:
        return f'<MinOfInterval: interval={self.time_series.period}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Min Of Interval:'
        yield from super().describe(indent)


class MeanOfIntervalOperation(TimeDurationSeriesOperationBase):

    @override
    def on_values(self, obj: Sequence[tuple[float, float]]) -> float | None:
        time = 0.0
        mean = 0.0
        for value, duration in obj:
            mean += value * duration
            time += duration

        if time <= 0:
            return None
        return mean / time

    def __repr__(self) -> str:
        return f'<MeanOfInterval: interval={self.time_series.period}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Mean Of Interval:'
        yield from super().describe(indent)
