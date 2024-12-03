from collections.abc import Generator
from math import ceil, floor
from typing import Final, Literal

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

        return round(value, self.digits)

    def __repr__(self) -> str:
        return f'<Round: {self.digits if self.digits is not None else 0} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Round: {self.digits if self.digits is not None else "integer"}'


class RoundToMultipleOperation(ValueOperationBase):
    # noinspection PyShadowingBuiltins
    def __init__(self, value: int, round: Literal['up', 'down', 'nearest']) -> None:   # noqa: A002
        self.multiple: Final = value

        self.round_up: Final = round == 'up'
        self.round_down: Final = round == 'down'

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.round_up:
            return self.multiple * int(ceil(value / self.multiple))
        if self.round_down:
            return self.multiple * int(floor(value / self.multiple))

        multiple = self.multiple
        div, rest = divmod(value, multiple)
        div = int(div)

        if rest >= 0.5 * multiple:
            return (div + 1) * multiple
        return div * multiple

    def __mode_str(self) -> str:
        if self.round_up:
            return 'up'
        if self.round_down:
            return 'down'
        return 'nearest'

    def __repr__(self) -> str:
        return f'<RoundToMultiple: value={self.multiple} round={self.__mode_str()} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Round To Multiple:'
        yield f'{indent:s}      value: {self.multiple}'
        yield f'{indent:s}      round: {self.__mode_str()}'
