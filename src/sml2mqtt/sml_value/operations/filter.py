from collections.abc import Generator
from time import monotonic
from typing import Final

from typing_extensions import override

from sml2mqtt.const import DurationType, get_duration
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase
from sml2mqtt.sml_value.operations._helper import format_period


class OnChangeFilterOperation(ValueOperationBase):
    def __init__(self):
        self.last_value: int | float | str | None = None

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.last_value == value:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<OnChange at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- On Change Filter'


class DeltaFilterBase(ValueOperationBase):
    def __init__(self, delta: int | float):
        self.delta: Final = delta
        self.last_value: int | float = -1_000_000_000   # random value which we are unlikely to hit


class AbsDeltaFilterOperation(DeltaFilterBase):
    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if abs(value - self.last_value) < self.delta:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<AbsDelta: {self.delta} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Delta Filter: {self.delta}'


class PercDeltaFilterOperation(DeltaFilterBase):
    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        perc = abs(1 - value / self.last_value) * 100
        if perc < self.delta:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<PercDelta: {self.delta}% at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Delta Filter: {self.delta}%'


class SkipZeroMeterOperation(ValueOperationBase):

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None or value < 0.1:
            return None
        return value

    def __repr__(self):
        return f'<SkipZeroMeter at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Zero Meter Filter'


class HeartbeatFilterOperation(ValueOperationBase):
    def __init__(self, every: DurationType):
        self.every: Final = get_duration(every)
        self.last_time: float = -1_000_000_000
        self.last_value: float | None = None

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is not None:
            self.last_value = value

        if monotonic() - self.last_time < self.every:
            return None

        self.last_time = monotonic()
        return self.last_value

    def __repr__(self):
        return f'<Heartbeat: {self.every}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Heartbeat Filter: {format_period(self.every)}'
