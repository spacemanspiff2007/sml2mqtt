from __future__ import annotations

from typing import TypeAlias, Any

from easyconfig import BaseModel
from pydantic import (
    Field,
    StrictBool,
    conlist, model_validator,
)

from .types import Number, TimeInSeconds, ObisHex  # noqa: TCH001


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
        description='Filter which lets a value pass periodically so that the value gets published '
                    'every specified interval.'
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
class OrOperation(BaseModel):
    operations: OperationsListType = Field(
        alias='or', description='A sequence of operations that will be evaluated one after another. '
                                'As soon as one operation returns a value the sequence will be aborted and '
                                'the returned value will be used.'
    )


class SequenceOperation(BaseModel):
    operations: OperationsListType = Field(
        alias='sequence', description='A sequence of operations that will be evaluated one after another. '
                                      'As soon as one operation blocks a value the whole sequence will be aborted and'
                                      'will return nothing.'
    )


OperationsType: TypeAlias = (
        OnChangeFilter | DeltaFilter | HeartbeatFilter |
        Factor | Offset | Round |
        NegativeOnEnergyMeterWorkaround |
        OrOperation | SequenceOperation
)

OperationsListType = conlist(item_type=OperationsType, min_length=1)
