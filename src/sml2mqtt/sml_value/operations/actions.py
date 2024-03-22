from collections.abc import Generator
from time import monotonic
from typing import Final

from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase
from sml2mqtt.sml_value.operations._helper import format_period


class RefreshActionOperation(ValueOperationBase):
    def __init__(self, every: int | float):
        self.every: Final = every
        self.last_time: float = -1
        self.last_value: float | None = None

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is not None:
            self.last_value = value
            self.last_time = monotonic()
            return value

        if monotonic() - self.last_time < self.every:
            return None

        self.last_time = monotonic()
        return self.last_value

    def __repr__(self):
        return f'<RefreshAction: {self.every}s at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Refresh Action: {format_period(self.every)}'
