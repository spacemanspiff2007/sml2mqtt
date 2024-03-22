import logging

import pytest

from sml2mqtt.config.config import GeneralSettings
from sml2mqtt.config.device import SmlDeviceConfig, SmlValueConfig
from sml2mqtt.config.operations import OnChangeFilter
from sml2mqtt.sml_device import SmlDevice
from sml2mqtt.sml_device.setup_device import setup_device
from sml2mqtt.sml_value.operations import OnChangeFilterOperation


@pytest.mark.ignore_log_warnings()
def test_warnings(no_mqtt, caplog, sml_frame_1_values):
    device = SmlDevice('test_device')
    device.mqtt_device.cfg.topic_full = 'test_device/device_id'

    device_cfg = SmlDeviceConfig(
        skip={'0100000009ff'},
        values=[
            SmlValueConfig(obis='0100000009ff', operations=[{'type': 'change filter'}])
        ]
    )
    general_cfg = GeneralSettings()

    setup_device(device, sml_frame_1_values, device_cfg, general_cfg)

    # This is what will be reported
    msg = "\n".join(x.msg for x in filter(lambda x: x.name == 'sml.test_device' and x.levelno == logging.WARNING, caplog.records))

    assert '\n' + msg + '\n' == """
Config for 0100000009ff found but 0100000009ff is also marked to be skipped
Config for 0100000009ff found but 0100000009ff was not reported by the frame
"""
