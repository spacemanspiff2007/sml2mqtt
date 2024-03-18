from collections.abc import Generator
from typing import Final

from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class FactorOperation(ValueOperationBase):
    def __init__(self, factor: int | float):
        self.factor: Final = factor

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        return value * self.factor

    def __repr__(self):
        return f'<Factor: {self.factor} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Factor: {self.factor}'


class OffsetOperation(ValueOperationBase):
    def __init__(self, offset: int | float):
        self.offset: Final = offset

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        return value + self.offset

    def __repr__(self):
        return f'<Offset: {self.offset} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Offset: {self.offset}'


class RoundOperation(ValueOperationBase):
    def __init__(self, digits: int):
        self.digits: Final = digits if digits else None

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if isinstance(value, int):
            return value
        return round(value, self.digits)

    def __repr__(self):
        return f'<Round: {self.digits if self.digits is not None else 0} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Round: {self.digits if self.digits is not None else "integer"}'


class LimitValueOperation(ValueOperationBase):
    # noinspection PyShadowingBuiltins
    def __init__(self, min: float | None, max: float | None, ignore: bool = False):  # noqa: A002
        self.min: Final = min
        self.max: Final = max
        self.ignore: Final = ignore

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        if self.min is not None and value < self.min:
            return self.min if not self.ignore else None

        if self.max is not None and value > self.max:
            return self.max if not self.ignore else None

        return value

    def __repr__(self):
        return f'<LimitValue: min={self.min} max={self.max} ignore={self.ignore} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Limit value:'
        if self.min is not None:
            yield f'{indent:s}    min: {self.min}'
        if self.max is not None:
            yield f'{indent:s}    max: {self.max}'
        yield f'{indent:s}    ignore out of range: {self.ignore}'
