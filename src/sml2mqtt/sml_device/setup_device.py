from __future__ import annotations

from typing import TYPE_CHECKING

from sml2mqtt.mqtt import BASE_TOPIC, check_for_duplicate_topics
from sml2mqtt.sml_value import SmlValue
from sml2mqtt.sml_value.operations import (
    FactorOperation,
    OffsetOperation,
    OnChangeFilterOperation,
    OrOperation,
    RangeFilterOperation,
    RefreshActionOperation,
    RoundOperation,
    SequenceOperation,
    SkipZeroMeterOperation,
)
from sml2mqtt.sml_value.setup_operations import setup_operations


if TYPE_CHECKING:
    import logging

    from sml2mqtt.config.config import GeneralSettings
    from sml2mqtt.config.device import SmlDeviceConfig
    from sml2mqtt.const import SmlFrameValues
    from sml2mqtt.sml_device import SmlDevice
    from sml2mqtt.sml_value.base import OperationContainerBase, ValueOperationBase


def has_operation_type(obj: OperationContainerBase, *ops: type[ValueOperationBase],
                       is_of: bool = True) -> ValueOperationBase | None:
    for op in obj.operations:
        if isinstance(op, ops) == is_of:
            return op
        if (isinstance(op, (OrOperation, SequenceOperation)) and
                (ret := has_operation_type(op, is_of=is_of)) is not None):
            return ret
    return None


def _create_default_transformations(log: logging.Logger, sml_value: SmlValue, frame: SmlFrameValues,
                                    general_cfg: GeneralSettings) -> None:

    op_count = len(sml_value.operations)

    if (entry := frame.get_value(sml_value.obis)) is not None and entry.unit == 30:
        if general_cfg.wh_in_kwh:
            if op := has_operation_type(sml_value, FactorOperation):
                log.debug(f'Found {op.__class__.__name__:s} - skip creating default factor')
            else:
                sml_value.insert_operation(FactorOperation(1 / 1000))

        # If the user has created something for the meter we don't skip it
        if not op_count:
            sml_value.insert_operation(SkipZeroMeterOperation())


def _create_default_filters(log: logging.Logger, sml_value: SmlValue, general_cfg: GeneralSettings):
    if op := has_operation_type(
        sml_value,
        FactorOperation, OffsetOperation, RoundOperation, RangeFilterOperation, SkipZeroMeterOperation,
        is_of=False
    ):
        log.debug(f'Found {op.__class__.__name__:s} - skip creating default filters')
        return None

    log.info(f'No filters found for {sml_value.obis}, creating default filters')

    sml_value.add_operation(OnChangeFilterOperation())
    sml_value.add_operation(RefreshActionOperation(general_cfg.republish_after))


def setup_device(device: SmlDevice, frame: SmlFrameValues, cfg: SmlDeviceConfig | None, general_cfg: GeneralSettings) -> None:
    mqtt_device = device.mqtt_device
    skip_default_setup = set()

    mqtt_device.set_topic(device.device_id)

    if cfg is not None:
        # mqtt of device
        mqtt_device.set_config(cfg.mqtt)
        device.mqtt_status.set_config(cfg.status)

        skipped_obis = set(cfg.skip)
        if not general_cfg.report_device_id and device.device_id is not None:
            skipped_obis.update(general_cfg.device_id_obis)

        device.sml_values.set_skipped(*skipped_obis)
        skip_default_setup.update(skipped_obis)

        for value_cfg in cfg.values:
            obis = value_cfg.obis
            skip_default_setup.add(obis)

            if obis in cfg.skip:
                device.log.warning(f'Config for {obis:s} found but {obis:s} is also marked to be skipped')
            if obis not in frame.obis_ids():
                device.log.warning(f'Config for {obis:s} found but {obis:s} was not reported by the frame')

            sml_value = SmlValue(
                obis,
                mqtt_device.create_child(topic_fragment=obis).set_config(value_cfg.mqtt)
            )
            device.sml_values.add_value(sml_value)

            setup_operations(sml_value, value_cfg)
            _create_default_transformations(device.log, sml_value, frame, general_cfg)
            _create_default_filters(device.log, sml_value, general_cfg)
    else:
        # No config found -> ignore defaults
        device.sml_values.set_skipped(*general_cfg.device_id_obis)

    # Create default for not
    for obis, _ in frame.items(skip=skip_default_setup):    # noqa: PERF102
        sml_value = SmlValue(obis, mqtt_device.create_child(topic_fragment=obis))
        device.sml_values.add_value(sml_value)

        _create_default_transformations(device.log, sml_value, frame, general_cfg)
        _create_default_filters(device.log, sml_value, general_cfg)

    # Check for duplicate MQTT topics
    check_for_duplicate_topics(BASE_TOPIC)
