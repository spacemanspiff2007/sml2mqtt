from time import monotonic
from typing import Final

from sml2mqtt.const import SmlFrameValues
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class SmlValue:
    def __init__(self, obis: str, mqtt: MqttObj):

        self.obis: Final = obis
        self.mqtt: Final = mqtt

        self.operations: tuple[ValueOperationBase, ...] = ()

        self.last_publish: float = 0

    def process_frame(self, frame: SmlFrameValues):
        if (sml_value := frame.get_value(self.obis)) is None:
            return None

        info = SmlValueInfo(sml_value, frame, self.last_publish)
        value = sml_value.get_value()

        for op in self.operations:
            if (value := op.process_value(value, info)) is None:
                break

        if value is None:
            return None

        self.mqtt.publish(value)
        self.last_publish = monotonic()

    def add_operation(self, operation: ValueOperationBase):
        self.operations = (*self.operations, operation)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} obis={self.obis} at 0x{id(self):x}>'
