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


def create_OnChangeFilter(change: Any): # noqa: 802
    return OnChangeFilterOperation()


def create_DeltaFilter(delta: int | float, is_percent: bool): # noqa: 802
    if is_percent:
        return PercDeltaFilterOperation(delta=delta)

    return AbsDeltaFilterOperation(delta=delta)


def create_VirtualMeter(model: VirtualMeter): # noqa: 802
    dows, days = model.get_dows_and_days()
    finder = DateTimeFinder()
    for time in model.times:
        finder.add_time(time)
    for dow in dows:
        finder.add_dow(dow)
    for day in days:
        finder.add_day(day)
    return VirtualMeterOperation(finder, start_now=model.start_now)


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
    OnChangeFilter: create_OnChangeFilter,
    HeartbeatFilter: HeartbeatFilterOperation,
    RefreshAction: RefreshActionOperation,
    DeltaFilter: create_DeltaFilter,

    Factor: FactorOperation,
    Offset: OffsetOperation,
    Round: RoundOperation,

    NegativeOnEnergyMeterWorkaround: create_workaround_negative_on_energy_meter,

    Or: create_or,
    Sequence: create_sequence,

    VirtualMeter: create_VirtualMeter
}


def get_operation_factory(obj: BaseModel) -> Callable:
    for cfg_type, func in MAPPING.items():
        if isinstance(obj, cfg_type):
            return func
    msg = f'Unknown operation configuration type {type(obj)}'
    raise ValueError(msg)


class _HasOperationsProto(Protocol):
    operations: list[BaseModel]


def setup_operations(parent: OperationContainerBase, cfg_parent: _HasOperationsProto):
    for cfg in cfg_parent.operations:
        factory = get_operation_factory(cfg)

        signature = get_signature(factory)
        pass_model = list(signature.parameters) == ['model']

        if (operation_obj := factory(**(cfg.model_dump() if not pass_model else {'model': cfg}))) is None:
            continue

        assert isinstance(operation_obj, ValueOperationBase)
        parent.add_operation(operation_obj)

        if isinstance(operation_obj, (OrOperation, SequenceOperation)):
            setup_operations(operation_obj, cfg)
