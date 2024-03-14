from collections.abc import Generator
from time import monotonic
from typing import Final

from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class OnChangeFilterOperation(ValueOperationBase):
    def __init__(self):
        self.last_value: int | float | str | None = None

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if self.last_value == value:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<OnChange at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- OnChangeFilter'


class DeltaFilterBase(ValueOperationBase):
    def __init__(self, change: int | float):
        self.change: Final = change
        self.last_value: int | float = -1_000_000_000   # random value which we are unlikely to hit


class AbsDeltaFilter(DeltaFilterBase):
    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if abs(value - self.last_value) < self.change:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<AbsDelta: {self.change} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- DeltaFilter: {self.change}'


class PercDeltaFilter(DeltaFilterBase):
    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        perc = abs(1 - value / self.last_value) * 100
        if perc < self.change:
            return None

        self.last_value = value
        return value

    def __repr__(self):
        return f'<PercDelta: {self.change}% at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- DeltaFilter: {self.change}%'


class HeartbeatFilterOperation(ValueOperationBase):
    def __init__(self, every: int | float):
        self.every: Final = every

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if monotonic() - info.last_pub < self.every:
            return None
        return value

    def __repr__(self):
        return f'<Heartbeat: {self.every}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- HeartbeatFilter: {self.every}s'


class SkipZeroMeterOperation(ValueOperationBase):

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if value < 0.1:
            return None
        return value

    def __repr__(self):
        return f'<SkipZeroMeter at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- ZeroMeterFilter'
