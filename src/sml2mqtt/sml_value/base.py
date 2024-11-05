from __future__ import annotations

from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    from collections.abc import Generator

    from smllib.sml import SmlListEntry

    from sml2mqtt.const import SmlFrameValues


class SmlValueInfo:
    __slots__ = ('value', 'frame', 'last_pub')

    def __init__(self, sml: SmlListEntry, frame: SmlFrameValues, last_pub: float) -> None:
        self.value: Final = sml
        self.frame: Final = frame

        self.last_pub: Final = last_pub

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} obis={self.value.obis}>'


class ValueOperationBase:
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        raise NotImplementedError()

    def describe(self, indent: str = '') -> Generator[str, None, None]:
        raise NotImplementedError()


class OperationContainerBase:
    def __init__(self) -> None:
        self.operations: tuple[ValueOperationBase, ...] = ()

    def add_operation(self, operation: ValueOperationBase):
        self.operations = (*self.operations, operation)
        return self

    def insert_operation(self, operation: ValueOperationBase):
        self.operations = (operation, *self.operations)
        return self


class ValueOperationWithStartupBase(ValueOperationBase):
    _PROCESS_VALUE_BACKUP_ATTR: Final = '_process_value_original'

    def on_first_value(self, value: float, info: SmlValueInfo):
        raise NotImplementedError()

    def enable_on_first_value(self) -> None:
        name: Final = self._PROCESS_VALUE_BACKUP_ATTR
        if hasattr(self, name):
            raise ValueError()

        setattr(self, name, self.process_value)
        self.process_value = self._process_value_first

    def _process_value_first(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        # restore original function
        name: Final = self._PROCESS_VALUE_BACKUP_ATTR
        self.process_value = getattr(self, name)
        delattr(self, name)

        return self.on_first_value(value, info)
