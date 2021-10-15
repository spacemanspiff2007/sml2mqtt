from typing import TypeVar

from sml2mqtt.value.__types__ import VALUE_TYPE


class FilterBase:
    def required(self, value: VALUE_TYPE) -> VALUE_TYPE:
        raise NotImplementedError()

    def done(self, value):
        raise NotImplementedError()


FILTER_OBJ = TypeVar('FILTER_OBJ', bound=FilterBase)
