from collections.abc import Generator
from time import monotonic
from typing import Final

from typing_extensions import override

from sml2mqtt.const import DurationType, get_duration
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase
from sml2mqtt.sml_value.operations._helper import format_period


class OnChangeFilterOperation(ValueOperationBase):
    def __init__(self) -> None:
        self.last_value: int | float | str | None = None

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.last_value == value:
            return None

        self.last_value = value
        return value

    def __repr__(self) -> str:
        return f'<OnChangeFilter at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- On Change Filter'


class RangeFilterOperation(ValueOperationBase):
    # noinspection PyShadowingBuiltins
    def __init__(self, min_value: float | None, max_value: float | None, limit_values: bool = True) -> None:
        self.min_value: Final = min_value
        self.max_value: Final = max_value
        self.limit_values: Final = limit_values

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if (min_value := self.min_value) is not None and value < min_value:
            return min_value if self.limit_values else None

        if (max_value := self.max_value) is not None and value > max_value:
            return max_value if self.limit_values else None

        return value

    def __repr__(self) -> str:
        return (f'<RangeFilter: min={self.min_value} max={self.max_value} '
                f'limit_values={self.limit_values} at 0x{id(self):x}>')

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Range Filter:'
        if self.min_value is not None:
            yield f'{indent:s}    min: {self.min_value}'
        if self.max_value is not None:
            yield f'{indent:s}    max: {self.max_value}'
        yield f'{indent:s}    limit to min/max: {self.limit_values}'


class DeltaFilterOperation(ValueOperationBase):
    def __init__(self, min_value: int | float | None = None, min_percent: int | float | None = None) -> None:
        self.min_value: Final = min_value
        self.min_percent: Final = min_percent

        self.last_value: int | float = -1_000_000_000

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        last_value = self.last_value

        diff = abs(value - last_value)

        if (delta_min := self.min_value) is not None and diff < delta_min:
            return None

        if (min_percent := self.min_percent) is not None:  # noqa: SIM102
            # if last value == 0 the percentual change is infinite and we always pass
            if last_value != 0:
                percent = abs(diff / last_value) * 100
                if percent < min_percent:
                    return None

        self.last_value = value
        return value

    def __repr__(self) -> str:
        return f'<DeltaFilter: min={self.min_value} min_percent={self.min_percent} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Delta Filter:'
        if self.min_value:
            yield f'{indent:s}    Min  : {self.min_value}'
        if self.min_percent:
            yield f'{indent:s}    Min %: {self.min_percent}'


class SkipZeroMeterOperation(ValueOperationBase):

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None or value < 0.1:
            return None
        return value

    def __repr__(self) -> str:
        return f'<SkipZeroMeter at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Zero Meter Filter'


class ThrottleFilterOperation(ValueOperationBase):
    def __init__(self, period: DurationType) -> None:
        self.period: Final = get_duration(period)
        self.last_time: float = -1_000_000_000

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        now = monotonic()
        if self.last_time + self.period > now:
            return None

        self.last_time = now
        return value

    def __repr__(self) -> str:
        return f'<ThrottleFilter: {self.period}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Throttle Filter: {format_period(self.period)}'
