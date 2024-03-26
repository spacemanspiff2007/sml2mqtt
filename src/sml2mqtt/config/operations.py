from __future__ import annotations

from datetime import date, time, timedelta
from enum import Enum
from typing import Annotated, Any, Final, Literal, TypeAlias, TypedDict, Union, final
from typing import get_args as _get_args

from annotated_types import Len
from easyconfig import BaseModel
from pydantic import Discriminator, Field, StrictBool, StrictFloat, StrictInt, Tag

from sml2mqtt.const import DateTimeFinder, DurationType, TimeSeries

from .types import Number, ObisHex, PercentStr  # noqa: TCH001


class EmptyKwargs(TypedDict):
    pass


# -------------------------------------------------------------------------------------------------
# Filters
# -------------------------------------------------------------------------------------------------
class OnChangeFilter(BaseModel):
    """A filter which lets the value only pass when it's different from the value that was passed the last time"""
    type: Literal['change filter'] = Field(description='Filter which passes only changes')

    @final
    def get_kwargs_on_change(self) -> EmptyKwargs:
        return {}


class DeltaFilterKwargs(TypedDict):
    delta: int | float
    is_percent: bool


class DeltaFilter(BaseModel):
    """A filter which lets the value only pass if the incoming value is different enough from value that was passed the
    last time. The delta can be specified as an absolute value or as a percentage.
    """

    delta: StrictInt | StrictFloat | PercentStr = Field(
        alias='delta filter',
        description='Absolute value or a percentage'
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
    """A filter which lets a value pass periodically every specified interval."""

    every: DurationType = Field(
        alias='heartbeat filter',
        description='Interval'
    )


# -------------------------------------------------------------------------------------------------
# Actions
# -------------------------------------------------------------------------------------------------
class RefreshAction(BaseModel):
    """Action which lets every value pass. When no value is received (e.g. because an earlier filter blocks)
    this action will produce the last received value every interval.
    """
    every: DurationType = Field(alias='refresh action', description='Refresh interval')


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
    """Limits the value to always be in a certain range

    """
    type: Literal['limit value']
    min: float | None = Field(None, description='minimum value')
    max: float | None = Field(None, description='maximum value')
    ignore: bool = Field(
        False, alias='ignore out of range', description='Instead of limiting the value it will be ignored'
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
    """Make value negative based on an energy meter status."""

    enabled_or_obis: StrictBool | ObisHex = Field(
        alias='negative on energy meter status',
        description='Set to "true" to enable or to "false" to disable workaround. '
                    'If the default obis code for the energy meter is wrong set '
                    'to the appropriate meter obis code instead'
    )


# -------------------------------------------------------------------------------------------------
# Operations
# -------------------------------------------------------------------------------------------------
class Or(BaseModel):
    """A sequence of operations that will be evaluated one after another. The first value that gets returned by an
    operation will be used.
    """
    operations: OperationsListType = Field(alias='or')


class Sequence(BaseModel):
    """A sequence of operations that will be evaluated one after another.
    If one operation blocks this will return nothing.
    """
    operations: OperationsListType = Field(alias='sequence')


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
class HasDateTimeFields(BaseModel):

    start_now: bool = Field(
        alias='start now', description='Immediately start instead of starting after the next reset'
    )
    reset_times: list[time] = Field(
        default=[], alias='reset times', description='Time(s) of day when a reset will occur',
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


class DateTimeBoundKwargs(TypedDict):
    start_now: bool
    dt_finder: DateTimeFinder


class VirtualMeter(HasDateTimeFields):
    """A virtual meter. It will output the difference from the last reset"""
    type: Literal['meter']


class MaxValue(HasDateTimeFields):
    """Maximum value since last reset"""
    type: Literal['max value']


class MinValue(HasDateTimeFields):
    """Minimum value since last reset"""
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
    """Maximum value in a sliding interval"""
    type: Literal['max interval']


class MinOfInterval(HasIntervalFields):
    """Minimum value in a sliding interval"""
    type: Literal['min interval']


class MeanOfInterval(HasIntervalFields):
    """Weighted mean in a sliding interval"""
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
