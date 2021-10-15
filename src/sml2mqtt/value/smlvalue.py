from typing import Dict, Final, Iterable, Optional, Union

from smllib.sml import SmlListEntry

from sml2mqtt.mqtt import MqttObj
from sml2mqtt.value.filter import FILTER_OBJ
from sml2mqtt.value.transformations import TRANSFORM_OBJ
from sml2mqtt.value.workarounds import WORKAROUND_OBJ


class SmlValue:
    def __init__(self, device: str, obis: str, mqtt: MqttObj,
                 workarounds: Iterable[WORKAROUND_OBJ],
                 transformations: Iterable[TRANSFORM_OBJ],
                 filters: Iterable[FILTER_OBJ]):

        self.device_id: Final = device
        self.obis: Final = obis
        self.mqtt: Final = mqtt

        self.sml_value: Optional[SmlListEntry] = None
        self.last_value: Union[None, int, float, str] = None

        self.workarounds: Final = workarounds
        self.transformations: Final = transformations
        self.filters: Final = filters

    def set_value(self, sml_value: Optional[SmlListEntry], frame_values: Dict[str, SmlListEntry]):
        self.sml_value = sml_value

        # apply all workarounds
        for workaround in self.workarounds:
            if workaround.enabled:
                sml_value = workaround.fix(sml_value, frame_values)

        # transform the values
        value = None if sml_value is None else sml_value.get_value()
        for f in self.transformations:
            value = f.process(value)
        self.last_value = value

        # check if we want to publish
        do_publish = False
        for refresh in self.filters:
            do_publish = refresh.required(value) or do_publish

        if not do_publish:
            return None

        self.mqtt.publish(value)
        for refresh in self.filters:
            refresh.done(value)

    def describe(self, indent=0, indent_width=2) -> str:

        base = " " * indent
        once = " " * (indent + indent_width)
        twice = " " * (indent + indent_width * 2)

        txt = f'{base}{self.mqtt.topic} ({self.obis}):\n' \
              f'{once}raw value: {self.sml_value.get_value()}\n' \
              f'{once}pub value: {self.last_value}\n'

        if self.workarounds:
            txt += f'{once}workarounds:\n'
            for w in self.workarounds:
                txt += f'{twice}- {w}\n'

        if self.transformations:
            txt += f'{once}transformations:\n'
            for t in self.transformations:
                txt += f'{twice}- {t}\n'

        if self.filters:
            txt += f'{once}filters:\n'
            for f in self.filters:
                txt += f'{twice}- {f}\n'

        return txt
