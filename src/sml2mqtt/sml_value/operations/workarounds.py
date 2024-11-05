from collections.abc import Generator
from typing import Final

from typing_extensions import override

from sml2mqtt.errors import RequiredObisValueNotInFrameError
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class NegativeOnEnergyMeterWorkaroundOperation(ValueOperationBase):
    def __init__(self, meter_obis: str | None = None) -> None:
        self.meter_obis: Final[str] = '0100010800ff' if meter_obis is None else meter_obis

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if (meter := info.frame.get_value(self.meter_obis)) is None:
            raise RequiredObisValueNotInFrameError(self.meter_obis)

        status = meter.status
        if not isinstance(status, int):
            msg = f'Energy Meter status {self.meter_obis:s} is not a valid int: {status} ({type(status)})'
            raise TypeError(msg)

        negative = status & 0x20
        if negative:
            value *= -1

        return value

    def __repr__(self) -> str:
        return f'<NegativeOnEnergyMeterWorkaround: {self.meter_obis:s} at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Negative On Status Of Energy Meter {self.meter_obis:s}'
