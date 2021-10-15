from typing import Final, Union

from .base import FilterBase, VALUE_TYPE


class DiffFilterBase(FilterBase):
    def __init__(self, min_diff: Union[int, float]):
        if min_diff < 0:
            raise ValueError('min diff must be >= 0')
        self.min_diff: Final = min_diff
        self.last_value: VALUE_TYPE = None

    def required(self, value: VALUE_TYPE) -> VALUE_TYPE:
        if value is None:
            return False
        if self.last_value is None:
            return True
        return self.diff(value)

    def done(self, value):
        self.last_value = value

    def diff(self, value: Union[int, float]) -> VALUE_TYPE:
        raise NotImplementedError()


class DiffAbsFilter(DiffFilterBase):
    def diff(self, value: Union[int, float]) -> VALUE_TYPE:
        if abs(value - self.last_value) < self.min_diff:
            return False
        return True

    def __repr__(self):
        return f'<AbsDiff: {self.min_diff}>'


class DiffPercFilter(DiffFilterBase):
    def diff(self, value: Union[int, float]) -> VALUE_TYPE:
        if not self.last_value:
            return False

        perc = abs(1 - value / self.last_value) * 100
        if perc < self.min_diff:
            return False
        return True

    def __repr__(self):
        return f'<PercDiff: {self.min_diff}>'
