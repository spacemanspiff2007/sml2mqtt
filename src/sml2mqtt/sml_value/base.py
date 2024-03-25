from __future__ import annotations

from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    from collections.abc import Generator

    from smllib.sml import SmlListEntry

    from sml2mqtt.const import SmlFrameValues


class SmlValueInfo:
    __slots__ = ('value', 'frame', 'last_pub')

    def __init__(self, sml: SmlListEntry, frame: SmlFrameValues, last_pub: float):
        self.value: Final = sml
        self.frame: Final = frame

        self.last_pub: Final = last_pub

    def __repr__(self):
        return f'<{self.__class__.__name__} obis={self.value.obis}>'


class ValueOperationBase:
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        raise NotImplementedError()

    def describe(self, indent: str = '') -> Generator[str, None, None]:
        raise NotImplementedError()


class OperationContainerBase:
    def __init__(self):
        self.operations: tuple[ValueOperationBase, ...] = ()

    def add_operation(self, operation: ValueOperationBase):
        self.operations = (*self.operations, operation)
        return self
