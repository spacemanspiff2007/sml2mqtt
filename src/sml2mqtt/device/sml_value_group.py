from __future__ import annotations

from typing import Final

from smllib.sml import SmlListEntry

from sml2mqtt.sml_value import SmlValue


class SmlValueGroup:
    def __init__(self, name: str):
        self.name: Final = name
        self.values: dict[str, SmlValue] = {}

    def process_frame(self, frame_values: dict[str, SmlListEntry]):
        for obis, frame_value in frame_values.items():
            value = self.values[obis]
            value.set_value(frame_value, frame_values)

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} {self.name:s}>'
