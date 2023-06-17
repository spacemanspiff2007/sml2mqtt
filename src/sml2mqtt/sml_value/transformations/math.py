from typing import Final, Union

from .base import TransformationBase, VALUE_TYPE
from sml2mqtt.__log__ import get_logger

class FactorTransformation(TransformationBase):
    def __init__(self, factor: Union[int, float]):
        self.factor: Final = factor

    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        if value is None:
            return None
        return value * self.factor

    def __repr__(self):
        return f'<Factor: {self.factor}>'


class OffsetTransformation(TransformationBase):
    def __init__(self, offset: Union[int, float]):
        self.offset: Final = offset

    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        if value is None:
            return None
        return value + self.offset

    def __repr__(self):
        return f'<Offset: {self.offset}>'


class RoundTransformation(TransformationBase):
    def __init__(self, digits: int):
        self.digits: Final = digits if digits else None

    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        return round(value, self.digits)

    def __repr__(self):
        return f'<Round: {self.digits if self.digits is not None else 0}>'


class MovingAverageTransformation(TransformationBase):
    def __init__(self, values: int):
        self.values: Final = values if values else 10

        self.buffer = []
        get_logger('mqtt').debug(f'MovingAverageTransformation.__init__({values})')

    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        # we need a number
        if not( isinstance(value, int) or isinstance(value, float)):
            return None

        self.buffer.append(value)
        if len(self.buffer) > self.values:
            self.buffer = self.buffer[-self.values:]

        avg = sum(self.buffer)/len(self.buffer)

        get_logger('mqtt').debug(f'MovingAverageTransformation.process({value} -> {self.buffer} -> {avg} ')

        return  avg

    def __repr__(self):
        return f'<MovingAverage: {self.values if self.values is not None else 0}>'
