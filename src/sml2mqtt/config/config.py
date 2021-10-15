from typing import Dict, List, Union

import pydantic
from easyconfig import AppConfigModel, ConfigModel
from pydantic import constr, Field

from .device import REPUBLISH_ALIAS, SmlDeviceConfig, SmlValueConfig
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig


class PortSettings(ConfigModel):
    url: constr(strip_whitespace=True, min_length=1, strict=True) = Field(..., description='Device path')
    timeout: Union[int, float] = Field(
        default=3, description='Seconds after which a timeout will be detected (default=3)')


class GeneralSettings(ConfigModel):
    wh_in_kwh: bool = Field(True, description='Automatically convert Wh to kWh', alias='Wh in kWh')
    republish_after: int = Field(
        120, description='Republish automatically after this time (if no other filter configured)',
        alias=REPUBLISH_ALIAS,
    )


class Settings(AppConfigModel):
    logging = LoggingSettings()
    mqtt = MqttConfig()
    general = GeneralSettings()
    ports: List[PortSettings] = [
        PortSettings(url='COM1', timeout=3),
        PortSettings(url='/dev/ttyS0', timeout=3),
    ]

    devices: Dict[str, SmlDeviceConfig] = Field(
        {}, description='Device configuration by ID or url',
        file_value={
            'DEVICE_ID_HEX': SmlDeviceConfig(
                mqtt=OptionalMqttPublishConfig(topic='DEVICE_BASE_TOPIC'),
                status=OptionalMqttPublishConfig(topic='status'),
                skip=['OBIS'],
                values={
                    'OBIS': SmlValueConfig(
                        mqtt=OptionalMqttPublishConfig(topic='OBIS'),
                        republish_after=120,
                        workarounds=[{'negative on energy meter status': True}],
                        transformations=[{'factor': 3}, {'offset': 100}, {'round': 2}],
                        filters=[{'diff': 10}, {'perc': 10}, {'every': 120}],
                    )
                }
            )
        }
    )


ConfigModel.Config.extra = pydantic.Extra.forbid

CONFIG = Settings()
