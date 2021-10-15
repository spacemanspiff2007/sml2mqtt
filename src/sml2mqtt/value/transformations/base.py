from typing import TypeVar

from sml2mqtt.value.__types__ import VALUE_TYPE


class TransformationBase:
    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        raise NotImplementedError()


TRANSFORM_OBJ = TypeVar('TRANSFORM_OBJ', bound=TransformationBase)
