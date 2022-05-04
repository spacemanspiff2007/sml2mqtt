import logging
from typing import Dict

from smllib.sml import SmlListEntry

import sml2mqtt
from sml2mqtt.__args__ import CMD_ARGS
from sml2mqtt.__log__ import get_logger
from sml2mqtt.value import SmlValue

VALUES: Dict[str, Dict[str, SmlValue]] = {}


values_log = get_logger('values')


def process_value(device: 'sml2mqtt.device.Device', obj: SmlListEntry, frame_values: Dict[str, SmlListEntry]):
    try:
        device_values = VALUES[device.device_id]
    except KeyError:
        VALUES[device.device_id] = device_values = {}

    try:
        value = device_values[str(obj.obis)]
    except KeyError:
        device_values[str(obj.obis)] = value = create_sml_value(device, obj)

    value.set_value(obj, frame_values)


def create_sml_value(device: 'sml2mqtt.device.Device', obj: SmlListEntry) -> SmlValue:
    obis = str(obj.obis)
    device_id = device.device_id
    log_level = logging.DEBUG if not CMD_ARGS.analyze else logging.INFO

    cfg = None
    if sml2mqtt.CONFIG.devices is not None:
        cfg = sml2mqtt.CONFIG.devices.get(device_id)

    def create_default_value():
        values_log.log(log_level, f'Creating default value handler for {device_id}/{obis}')
        return SmlValue(
            device_id, obis, device.mqtt_device.create_child(obis),
            workarounds=[],
            transformations=[],
            filters=sml2mqtt.value.filter_from_config(None)
        )

    if cfg is None or cfg.values is None:
        return create_default_value()

    value_cfg = cfg.values.get(obis)
    if value_cfg is None:
        return create_default_value()

    values_log.log(log_level, f'Creating value handler from config for {device_id}/{obis}')

    return SmlValue(
        device_id, obis, device.mqtt_device.create_child(obis).set_config(value_cfg.mqtt),
        workarounds=sml2mqtt.value.workaround_from_config(value_cfg.workarounds),
        transformations=sml2mqtt.value.transform_from_config(value_cfg.transformations),
        filters=sml2mqtt.value.filter_from_config(value_cfg.filters),
    )
