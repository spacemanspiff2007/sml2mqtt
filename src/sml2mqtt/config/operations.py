from __future__ import annotations

from datetime import date, time
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
    BeforeValidator, Discriminator, Tag, constr, field_validator
)
from pydantic_core import PydanticCustomError

from .types import Number, ObisHex, TimeInSeconds, LowerStr  # noqa: TCH001
from ..const import DateTimeFinder


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


class DeltaFilter(BaseModel):
    is_percent: bool = Field(False, exclude=True)

    delta: int | float = Field(
        alias='delta filter',
        description='Filter which passes only when the incoming value is different enough from the previously passed '
                    'value. Can be an absolute value or a percentage'
    )

    @model_validator(mode='before')
    @classmethod
    def _check_percentage(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key_percent = 'is_percent'
            key_delta = 'delta filter'

            if key_percent in data:
                msg = f'"{key_percent:s}" can not be set'
                raise ValueError(msg)

            if isinstance(delta := data.get(key_delta), str):
                delta = delta.strip()
                if delta.endswith('%'):
                    data[key_percent] = True
                    data[key_delta] = delta[:-1].strip()

        return data


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
        default=[], alias='reset times', description='Time(s) of day when the meter will reset', min_length=1,
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


# -------------------------------------------------------------------------------------------------

OperationsModels = (
        OnChangeFilter, DeltaFilter, HeartbeatFilter,
        RefreshAction,
        Factor, Offset, Round,
        NegativeOnEnergyMeterWorkaround,
        Or, Sequence,
        VirtualMeter
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

OperationsListType = Annotated[list[OperationsTypeAnnotated], Len(1)]


def cleanup_validation_errors(msg: str) -> str:
    # In the ValidationError there is the Model and the field, but the user should only be concerned by the field name
    return msg.replace('Or.or', 'or').replace('Sequence.sequence', 'sequence')
