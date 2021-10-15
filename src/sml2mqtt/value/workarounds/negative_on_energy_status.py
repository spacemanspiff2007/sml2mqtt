from typing import Dict

from smllib.sml import SmlListEntry

from .base import WORKAROUND_TYPE, WorkaroundBase


class NegativeOnEnergyMeterStatus(WorkaroundBase):
    def __init__(self, arg: WORKAROUND_TYPE):
        super().__init__(arg)

        self.meter_obis = '0100010800ff'
        if isinstance(arg, str):
            self.meter_obis = arg

    def fix(self, value: SmlListEntry, frame_values: Dict[str, SmlListEntry]) -> SmlListEntry:
        meter = frame_values.get(self.meter_obis)
        if meter is None:
            raise ValueError(f'Configured meter obis "{self.meter_obis}" not found in current frame')

        status = meter.status
        if not isinstance(status, int):
            raise ValueError(f'Energy Meter status is not a valid int: {status} ({type(status)})')

        negative = status & 0x20
        if negative:
            value.value *= -1
