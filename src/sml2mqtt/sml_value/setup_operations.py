from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel

from sml2mqtt.config.operations import (
    DeltaFilter,
    Factor,
    HeartbeatAction,
    MaxOfInterval,
    MaxValue,
    MeanOfInterval,
    MinOfInterval,
    MinValue,
    NegativeOnEnergyMeterWorkaround,
    Offset,
    OnChangeFilter,
    OperationsType,
    Or,
    RangeFilter,
    RefreshAction,
    Round,
    Sequence,
    ThrottleFilter,
    VirtualMeter,
)
from sml2mqtt.sml_value.base import OperationContainerBase, ValueOperationBase
from sml2mqtt.sml_value.operations import (
    DeltaFilterOperation,
    FactorOperation,
    HeartbeatActionOperation,
    MaxOfIntervalOperation,
    MaxValueOperation,
    MeanOfIntervalOperation,
    MinOfIntervalOperation,
    MinValueOperation,
    NegativeOnEnergyMeterWorkaroundOperation,
    OffsetOperation,
    OnChangeFilterOperation,
    OrOperation,
    RangeFilterOperation,
    RefreshActionOperation,
    RoundOperation,
    SequenceOperation,
    ThrottleFilterOperation,
    VirtualMeterOperation,
)


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
    HeartbeatAction: HeartbeatActionOperation,
    DeltaFilter: DeltaFilterOperation,

    RefreshAction: RefreshActionOperation,
    ThrottleFilter: ThrottleFilterOperation,

    Factor: FactorOperation,
    Offset: OffsetOperation,
    Round: RoundOperation,
    RangeFilter: RangeFilterOperation,

    NegativeOnEnergyMeterWorkaround: create_workaround_negative_on_energy_meter,

    Or: create_or,
    Sequence: create_sequence,

    VirtualMeter: VirtualMeterOperation,
    MinValue: MinValueOperation,
    MaxValue: MaxValueOperation,

    MaxOfInterval: MaxOfIntervalOperation,
    MinOfInterval: MinOfIntervalOperation,
    MeanOfInterval: MeanOfIntervalOperation,
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


def setup_operations(parent: OperationContainerBase, cfg_parent: _HasOperationsProto) -> None:
    for cfg in cfg_parent.operations:
        factory = get_operation_factory(cfg)

        if kwarg_names := get_kwargs_names(cfg):
            kwargs = {name: value for kwarg_name in kwarg_names for name, value in getattr(cfg, kwarg_name)().items()}
        else:
            kwargs = cfg.model_dump(exclude={'type'})

        if (operation_obj := factory(**kwargs)) is None:
            continue

        assert isinstance(operation_obj, ValueOperationBase)
        parent.add_operation(operation_obj)

        if isinstance(operation_obj, (OrOperation, SequenceOperation)):
            setup_operations(operation_obj, cfg)
