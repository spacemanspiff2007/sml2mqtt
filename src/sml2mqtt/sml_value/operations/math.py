from collections.abc import Generator
from typing import Final

from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class FactorOperation(ValueOperationBase):
    def __init__(self, factor: int | float) -> None:
        self.factor: Final = factor

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None
        return value * self.factor

    def __repr__(self) -> str:
        return f'<Factor: {self.factor} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Factor: {self.factor}'


class OffsetOperation(ValueOperationBase):
    def __init__(self, offset: int | float) -> None:
        self.offset: Final = offset

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None
        return value + self.offset

    def __repr__(self) -> str:
        return f'<Offset: {self.offset} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Offset: {self.offset}'


class RoundOperation(ValueOperationBase):
    def __init__(self, digits: int) -> None:
        self.digits: Final = digits if digits else None

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if isinstance(value, int):
            return value
        return round(value, self.digits)

    def __repr__(self) -> str:
        return f'<Round: {self.digits if self.digits is not None else 0} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Round: {self.digits if self.digits is not None else "integer"}'
