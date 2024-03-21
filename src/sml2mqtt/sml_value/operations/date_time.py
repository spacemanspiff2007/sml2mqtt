from collections.abc import Generator
from datetime import datetime
from typing import Final

from typing_extensions import override

from sml2mqtt.const import DateTimeFinder, get_now
from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class SupportsDateTimeAction(ValueOperationBase):
    _START_NOW_FUNC_ATTR = '_process_value_original'

    def __init__(self, dt_finder: DateTimeFinder, start_now: bool = True):
        self._dt_finder: Final = dt_finder
        self._next_reset: datetime = dt_finder.get_first_reset(start_now)

        if start_now or not self._dt_finder.enabled:
            assert not hasattr(self, self._START_NOW_FUNC_ATTR)
            setattr(self, self._START_NOW_FUNC_ATTR, self.process_value)
            self.process_value = self._process_value_start_now

    def start_now_logic(self, value, info: SmlValueInfo):
        raise NotImplementedError()

    def after_next_reset(self, update: bool = True) -> bool:
        if not self._dt_finder.enabled:
            return False

        if (now := get_now()) >= self._next_reset:
            if update:
                self._next_reset = self._dt_finder.calc_next(now)
            return True

        return False

    def _process_value_start_now(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        self.start_now_logic(value, info)

        # restore original function
        self.process_value = getattr(self, self._START_NOW_FUNC_ATTR)
        delattr(self, self._START_NOW_FUNC_ATTR)

        return self.process_value(value, info)

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        if not self._dt_finder.enabled:
            yield f'{indent:s}    No resets'
            return None

        yield f'{indent:s}    Next resets:'
        yield f'{indent:s}     - {self._next_reset}'

        next_dt = self._next_reset

        # for every condition we want to show two values
        samples = max(self._dt_finder.condition_count * 2 - 1, 2)
        for _ in range(samples):
            next_dt = self._dt_finder.calc_next(next_dt)
            yield f'{indent:s}     - {next_dt}'


class VirtualMeterOperation(SupportsDateTimeAction):
    def __init__(self, dt_finder: DateTimeFinder, start_now: bool = True):
        super().__init__(dt_finder, start_now)
        self.last_value: float | None = None
        self.offset: float | None = None

    def start_now_logic(self, value, info: SmlValueInfo):
        self.last_value = value
        self.offset = value

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.after_next_reset():
            self.offset = self.last_value

        self.last_value = value

        if (offset := self.offset) is None:
            return None

        return value - offset

    def __repr__(self):
        return (f'<VirtualMeter: next_reset={self._next_reset} offset={self.offset} '
                f'last_value={self.last_value} at 0x{id(self):x}>')

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Virtual meter:'
        yield f'{indent:s}    Offset: {self.offset}'
        yield from super().describe(indent)


class MaxValueOperation(SupportsDateTimeAction):
    def __init__(self, dt_finder: DateTimeFinder, start_now: bool = True):
        super().__init__(dt_finder, start_now)
        self.max_value: float | None = None

    def start_now_logic(self, value, info: SmlValueInfo):
        self.max_value = value

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.after_next_reset():
            self.max_value = value
            return value

        if self.max_value is None or value <= self.max_value:
            return None

        self.max_value = value
        return value

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Max value:'
        yield f'{indent:s}    max: {self.max_value}'
        yield from super().describe(indent)


class MinValueOperation(SupportsDateTimeAction):
    def __init__(self, dt_finder: DateTimeFinder, start_now: bool = True):
        super().__init__(dt_finder, start_now)
        self.min_value: float | None = None

    def start_now_logic(self, value, info: SmlValueInfo):
        self.min_value = value

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        if value is None:
            return None

        if self.after_next_reset():
            self.min_value = value
            return value

        if self.min_value is None or value >= self.min_value:
            return None

        self.min_value = value
        return value

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Min value:'
        yield f'{indent:s}    min: {self.min_value}'
        yield from super().describe(indent)
