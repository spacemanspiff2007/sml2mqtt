from typing import Final, Union

from .base import TransformationBase, VALUE_TYPE


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
