from __future__ import annotations

from datetime import date, time
from enum import Enum
from typing import Any, TypeAlias, Annotated
from typing import get_args as _get_args

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


# -------------------------------------------------------------------------------------------------
# Filters
# -------------------------------------------------------------------------------------------------
class OnChangeFilter(BaseModel):
    change: Any = Field(alias='change filter', description='Filter which passes only changes')


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


class RepublishFilter(BaseModel):
    every: TimeInSeconds = Field(
        alias='republish filter',
        description='Filter which lets every value pass. When no value is received '
                    '(e.g. because an earlier filter blocks) this filter will produce the last value every interval.'
                    'Makes only sense as the last filter.'
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
# VirtualMeter
# -------------------------------------------------------------------------------------------------
class VirtualMeter(BaseModel):
    start_now: bool = Field(
        alias='start now', description='Immediately start the virtual meter instead of after the next reset'
    )
    times: list[time] = Field(
        description='Time(s) of day when the meter will reset', min_length=1,
    )
    days: list[DayOfMonth | DayOfWeekStr] = Field(
        description='Days of month or weekdays where the time(s) will be checked'
    )

    def get_dows_and_days(self) -> tuple[list[int], list[int]]:
        names = generate_day_names()
        return [names[n] for n in self.days if not isinstance(n, int)], [n for n in self.days if isinstance(n, int)]


# OperationsType: TypeAlias = (
#         Annotated[OnChangeFilter, Tag('OnChangeFilter')] |
#         Annotated[DeltaFilter, Tag('DeltaFilter')] |
#         Annotated[HeartbeatFilter, Tag('HeartbeatFilter')] |
#         Annotated[Factor, Tag('Factor')] |
#         Annotated[Offset, Tag('Offset')] |
#         Annotated[Round, Tag('Round')] |
#         Annotated[NegativeOnEnergyMeterWorkaround, Tag('NegativeOnEnergyMeterWorkaround')] |
#         Annotated[Or, Tag('Or')] |
#         Annotated[Sequence, Tag('Sequence')]
# )
#
#
# KEYS_TO_TAG: dict[tuple[str, ...], str] = {
#     (_f.alias if _f.alias is not None else _n): _m.__class__.__name__
#     for _m in _get_args(OperationsType) for _n, _f in _m.model_fields.items() if _f.exclude is not True
# }
#
# ALLOWED_KEYS: tuple[str, ...] = tuple(sorted({key for keys in KEYS_TO_TAG for key in keys}))
#
#
# def check_allowed_keys(obj: Any):
#     if isinstance(obj, dict):
#         return KEYS_TO_TAG.get(tuple(obj))
#
#     if isinstance(obj, BaseModel):
#         return KEYS_TO_TAG.get(tuple(obj.model_fields))
#
#     return None
#
#
# OperationsTypeAnnotated: TypeAlias = Annotated[
#     OperationsType,
#     Discriminator(
#         check_allowed_keys,
#         custom_error_type='invalid_field_names',
#         custom_error_message='Invalid field names',
#         custom_error_context={'discriminator': 'check_allowed_keys'}
#     )
# ]
#
# OperationsListType = Annotated[list[OperationsTypeAnnotated], Len(1)]


OperationsType: TypeAlias = (
        OnChangeFilter | DeltaFilter | HeartbeatFilter |
        Factor | Offset | Round |
        NegativeOnEnergyMeterWorkaround |
        Or | Sequence |
        VirtualMeter
)

OperationsListType = conlist(item_type=OperationsType, min_length=1)
