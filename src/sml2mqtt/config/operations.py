from __future__ import annotations

from datetime import date, time, timedelta
from enum import Enum
from typing import Any, TypeAlias, Annotated, Union, Final, Literal, TypedDict, final
from typing import get_args as _get_args
from typing_extensions import override

from annotated_types import Len
from easyconfig import BaseModel
from pydantic import (
    Field,
    StrictBool,
    conlist,
    model_validator,
    BeforeValidator, Discriminator, Tag, constr, field_validator, Strict, StringConstraints, StrictInt, StrictFloat
)
from pydantic_core import PydanticCustomError

from .types import Number, ObisHex, TimeInSeconds, LowerStr  # noqa: TCH001
from ..const import DateTimeFinder, TimeSeries


class EmptyKwargs(TypedDict):
    pass


# -------------------------------------------------------------------------------------------------
# Filters
# -------------------------------------------------------------------------------------------------
class OnChangeFilter(BaseModel):
    change: Any = Field(alias='change filter', description='Filter which passes only changes')

    @final
    def get_kwargs_on_change(self) -> EmptyKwargs:
        return {}


class DeltaFilterKwargs(TypedDict):
    delta: int | float
    is_percent: bool


PERCENT_STR = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r'^\d+\.?\d*\s*%$')]


class DeltaFilter(BaseModel):
    delta: StrictInt | StrictFloat | PERCENT_STR = Field(
        alias='delta filter',
        description='Filter which passes only when the incoming value is different enough from the previously passed '
                    'value. Can be an absolute value or a percentage'
    )

    @final
    def get_kwargs_delta(self) -> DeltaFilterKwargs:

        is_percent = False
        if isinstance(self.delta, str):
            delta = self.delta
            is_percent = delta.endswith('%')
            delta = delta.removesuffix('%')
            try:
                delta = int(delta)
            except ValueError:
                delta = float(delta)
        else:
            delta = self.delta

        return {
            'delta': delta,
            'is_percent': is_percent
        }


class HeartbeatFilter(BaseModel):
    every: TimeInSeconds = Field(
        alias='heartbeat filter',
        description='Filter which lets a value pass periodically every specified interval.'
    )


# -------------------------------------------------------------------------------------------------
# Actions
# -------------------------------------------------------------------------------------------------
class RefreshAction(BaseModel):
    every: TimeInSeconds = Field(
        alias='refresh action',
        description='Action which lets every value pass. When no value is received '
                    '(e.g. because an earlier filter blocks) this filter will produce the last value every interval.'
    )


# -------------------------------------------------------------------------------------------------
# Math
# -------------------------------------------------------------------------------------------------
class Factor(BaseModel):
    factor: Number = Field(description='Factor with which the value gets multiplied')


class Offset(BaseModel):
    offset: Number = Field(description='Offset that gets added on the value')


class Round(BaseModel):
    digits: int = Field(ge=0, le=6, alias='round', description='Round to the specified digits')


class LimitValue(BaseModel):
    type: Literal['limit value']
    min: float | None = Field(None, description='minimum value')
    max: float | None = Field(None, description='maximum value')
    ignore: bool = Field(
        False, alias='ignore out of range', description='Instead of limiting the value if it is out of range ignore it'
    )

    @final
    def get_kwargs_limit(self) -> LimitValueKwargs:
        return {
            'min': self.min,
            'max': self.max,
            'ignore': self.ignore
        }


class LimitValueKwargs(TypedDict):
    min: float | None
    max: float | None
    ignore: bool

# -------------------------------------------------------------------------------------------------
# Workarounds
# -------------------------------------------------------------------------------------------------
class NegativeOnEnergyMeterWorkaround(BaseModel):
    enabled_or_obis: StrictBool | ObisHex = Field(
        alias='negative on energy meter status',
        description='Make value negative based on an energy meter status. '
                    'Set to "true" to enable or to "false" to disable workaround. '
                    'If the default obis code for the energy meter is wrong set '
                    'to the appropriate meter obis code instead'
    )


# -------------------------------------------------------------------------------------------------
# Operations
# -------------------------------------------------------------------------------------------------
class Or(BaseModel):
    operations: OperationsListType = Field(
        alias='or', description='A sequence of operations that will be evaluated one after another.\n'
                                'As soon as one operation returns a value the sequence will be aborted and '
                                'the returned value will be used.'
    )


class Sequence(BaseModel):
    operations: OperationsListType = Field(
        alias='sequence', description='A sequence of operations that will be evaluated one after another.\n'
                                      'As soon as one operation blocks a value the whole sequence will be aborted and '
                                      'will return nothing.'
    )


def generate_day_names() -> dict[str, int]:
    # names of weekdays in local language
    day_names: dict[str, int] = {date(2001, 1, i).strftime('%A'): i for i in range(1, 8)}
    day_names.update({date(2001, 1, i).strftime('%A')[:3]: i for i in range(1, 8)})

    # abbreviations in German and English
    day_names.update({"Mo": 1, "Di": 2, "Mi": 3, "Do": 4, "Fr": 5, "Sa": 6, "So": 7})
    day_names.update({"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7})
    return {k.lower(): v for k, v in day_names.items()}


DayOfWeekStr = Enum('DayOfWeekStr', {k: k for k in generate_day_names()}, type=str)
DayOfMonth = Annotated[int, Field(ge=1, le=31, strict=True)]


# -------------------------------------------------------------------------------------------------
# DateTime
# -------------------------------------------------------------------------------------------------
class DateTimeBoundKwargs(TypedDict):
    start_now: bool
    dt_finder: DateTimeFinder


class HasDateTimeFields(BaseModel):

    start_now: bool = Field(
        alias='start now', description='Immediately start the virtual meter instead of after the next reset'
    )
    reset_times: list[time] = Field(
        default=[], alias='reset times', description='Time(s) of day when the meter will reset',
    )
    reset_days: list[DayOfMonth | DayOfWeekStr] = Field(
        default=[], alias='reset days', description='Days of month or weekdays where the time(s) will be checked'
    )

    @final
    def get_kwargs_dt_fields(self) -> DateTimeBoundKwargs:

        names = generate_day_names()
        dows = [names[n] for n in self.reset_days if not isinstance(n, int)]
        days = [n for n in self.reset_days if isinstance(n, int)]

        finder = DateTimeFinder()
        for t in self.reset_times:
            finder.add_time(t)
        for dow in dows:
            finder.add_dow(dow)
        for day in days:
            finder.add_day(day)

        return {
            'dt_finder': finder,
            'start_now': self.start_now
        }


class VirtualMeter(HasDateTimeFields):
    type: Literal['meter']


class MaxValue(HasDateTimeFields):
    type: Literal['max value']


class MinValue(HasDateTimeFields):
    type: Literal['min value']


# -------------------------------------------------------------------------------------------------
# TimeSeries
# -------------------------------------------------------------------------------------------------
class TimeSeriesKwargs(TypedDict):
    time_series: TimeSeries
    reset_after_value: bool


class HasIntervalFields(BaseModel):

    interval: timedelta = Field(
        description='Interval duration'
    )

    wait_for_data: bool = Field(
        alias='wait for data', description='Only produce a value when data for the whole interval is available'
    )

    reset_after_value: bool = Field(
        False, alias='reset after value', description='Clear all data as soon as a value has been produced'
    )

    @final
    def get_kwargs_interval_fields(self) -> TimeSeriesKwargs:
        return {
            'time_series': TimeSeries(self.interval, wait_for_data=self.wait_for_data),
            'reset_after_value': self.reset_after_value
        }


class MaxOfInterval(HasIntervalFields):
    type: Literal['max interval']


class MinOfInterval(HasIntervalFields):
    type: Literal['min interval']


class MeanOfInterval(HasIntervalFields):
    type: Literal['mean interval']


# -------------------------------------------------------------------------------------------------

OperationsModels = (
    OnChangeFilter, DeltaFilter, HeartbeatFilter,
    RefreshAction,
    Factor, Offset, Round, LimitValue,
    NegativeOnEnergyMeterWorkaround,
    Or, Sequence,
    VirtualMeter, MaxValue, MinValue,
    MaxOfInterval, MinOfInterval, MeanOfInterval,
)

# noinspection PyTypeHints
OperationsType: TypeAlias = Union[tuple(Annotated[o, Tag(o.__name__)] for o in OperationsModels)]  # noqa: UP007


MODEL_FIELD_MAP: Final[dict[str, frozenset[str]]] = {
    _m.__name__: frozenset(
        _f.alias if _f.alias is not None else _n for _n, _f in _m.model_fields.items() if _f.exclude is not True
    )
    for _m in OperationsModels
}

MODEL_TYPE_MAP: Final[str, str] = {
    _get_args(_f.annotation)[0]: _m.__name__
    for _m in OperationsModels for _n, _f in _m.model_fields.items() if _n == 'type'
}


def check_allowed_keys(obj: Any):
    if isinstance(obj, dict):
        type = obj.get('type')  # noqa: A001
        keys = set(obj)
    else:
        type = getattr(obj, 'type', None)  # noqa: A001
        keys = set(obj.model_fields)

    # we have a type field
    if type is not None:
        return MODEL_TYPE_MAP.get(type)

    # let's see if we have a 100% match
    for name, fields in MODEL_FIELD_MAP.items():
        if keys == fields:
            return name
    return None


OperationsTypeAnnotated: TypeAlias = Annotated[
    OperationsType,
    Discriminator(
        check_allowed_keys,
        custom_error_type='invalid_key_names',
        custom_error_message='Invalid key names',
        custom_error_context={'discriminator': 'check_allowed_keys'}
    )
]

OperationsListType = Annotated[list[OperationsTypeAnnotated], Len(min_length=1)]


def cleanup_validation_errors(msg: str) -> str:
    # In the ValidationError there is the Model and the field, but the user should only be concerned by the field name
    return msg.replace('Or.or', 'or').replace('Sequence.sequence', 'sequence')
