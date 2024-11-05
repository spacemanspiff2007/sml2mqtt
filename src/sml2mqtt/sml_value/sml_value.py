from collections.abc import Generator
from time import monotonic
from typing import Final

from sml2mqtt.const import SmlFrameValues
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.sml_value.base import OperationContainerBase, SmlValueInfo


class SmlValue(OperationContainerBase):
    def __init__(self, obis: str, mqtt: MqttObj) -> None:
        super().__init__()

        self.obis: Final = obis
        self.mqtt: Final = mqtt

        self.last_publish: float = 0

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} obis={self.obis} at 0x{id(self):x}>'

    def process_frame(self, frame: SmlFrameValues):
        if (sml_value := frame.get_value(self.obis)) is None:
            return None

        info = SmlValueInfo(sml_value, frame, self.last_publish)
        value = sml_value.get_value()

        for op in self.operations:
            value = op.process_value(value, info)

        if value is None:
            return None

        self.mqtt.publish(value)
        self.last_publish = monotonic()
        return value

    def describe(self) -> Generator[str, None, None]:
        yield f'<SmlValue>'
        yield f'  obis : {self.obis:s}'
        yield f'  topic: {self.mqtt.topic:s}'
        yield f'  operations:'
        for op in self.operations:
            yield from op.describe(f'    ')
        yield ''
