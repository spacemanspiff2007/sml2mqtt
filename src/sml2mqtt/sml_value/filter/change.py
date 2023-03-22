from .base import FilterBase, VALUE_TYPE


class ChangeFilter(FilterBase):
    def __init__(self):
        self.last_value: VALUE_TYPE = None

    def required(self, value: VALUE_TYPE) -> VALUE_TYPE:
        if self.last_value is None:
            return True

        if value != self.last_value:
            return True

        return False

    def done(self, value):
        self.last_value = value

    def __repr__(self):
        return '<OnChange>'
