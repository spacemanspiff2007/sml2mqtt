from collections.abc import Callable
from inspect import signature as get_signature
from typing import Any, Protocol

from pydantic import BaseModel

from sml2mqtt.config.operations import (
    DeltaFilter,
    Factor,
    HeartbeatFilter,
    NegativeOnEnergyMeterWorkaround,
    Offset,
    OnChangeFilter,
    OperationsType,
    Or,
    RefreshAction,
    Round,
    Sequence,
    VirtualMeter,
)
from sml2mqtt.sml_value.base import OperationContainerBase, ValueOperationBase
from sml2mqtt.sml_value.operations import (
    AbsDeltaFilterOperation,
    DateTimeFinder,
    FactorOperation,
    HeartbeatFilterOperation,
    NegativeOnEnergyMeterWorkaroundOperation,
    OffsetOperation,
    OnChangeFilterOperation,
    OrOperation,
    PercDeltaFilterOperation,
    RefreshActionOperation,
    RoundOperation,
    SequenceOperation,
    VirtualMeterOperation,
)


def create_DeltaFilter(delta: int | float, is_percent: bool): # noqa: 802
    if is_percent:
        return PercDeltaFilterOperation(delta=delta)

    return AbsDeltaFilterOperation(delta=delta)


def create_workaround_negative_on_energy_meter(enabled_or_obis: bool | str):
    if isinstance(enabled_or_obis, str):
        return NegativeOnEnergyMeterWorkaroundOperation(meter_obis=enabled_or_obis)
    if enabled_or_obis:
        return NegativeOnEnergyMeterWorkaroundOperation()
    return None


def create_or(operations: list[OperationsType]):
    return OrOperation()


def create_sequence(operations: list[OperationsType]):
    return SequenceOperation()


MAPPING = {
    OnChangeFilter: OnChangeFilterOperation,
    HeartbeatFilter: HeartbeatFilterOperation,
    DeltaFilter: create_DeltaFilter,

    RefreshAction: RefreshActionOperation,

    Factor: FactorOperation,
    Offset: OffsetOperation,
    Round: RoundOperation,

    NegativeOnEnergyMeterWorkaround: create_workaround_negative_on_energy_meter,

    Or: create_or,
    Sequence: create_sequence,

    VirtualMeter: VirtualMeterOperation
}


def get_operation_factory(obj: BaseModel) -> Callable:
    for cfg_type, func in MAPPING.items():
        if isinstance(obj, cfg_type):
            return func
    msg = f'Unknown operation configuration type {type(obj)}'
    raise ValueError(msg)


def get_kwargs_names(obj: BaseModel) -> list[str]:
    return [n for n in dir(obj) if n.startswith('get_kwargs_')]


class _HasOperationsProto(Protocol):
    operations: list[BaseModel]


def setup_operations(parent: OperationContainerBase, cfg_parent: _HasOperationsProto):
    for cfg in cfg_parent.operations:
        factory = get_operation_factory(cfg)

        if kwarg_names := get_kwargs_names(cfg):
            kwargs = {name: value for kwarg_name in kwarg_names for name, value in getattr(cfg, kwarg_name)().items()}
        else:
            kwargs = cfg.model_dump()

        if (operation_obj := factory(**kwargs)) is None:
            continue

        assert isinstance(operation_obj, ValueOperationBase)
        parent.add_operation(operation_obj)

        if isinstance(operation_obj, (OrOperation, SequenceOperation)):
            setup_operations(operation_obj, cfg)
