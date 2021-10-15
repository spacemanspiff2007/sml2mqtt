from typing import Dict, List, Union

import pydantic
from easyconfig import AppConfigMixin, ConfigMixin, create_app_config
from pydantic import BaseModel, constr, Field

from .device import REPUBLISH_ALIAS, SmlDeviceConfig, SmlValueConfig
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig


class PortSettings(BaseModel, ConfigMixin):
    url: constr(strip_whitespace=True, min_length=1, strict=True) = Field(..., description='Device path')
    timeout: Union[int, float] = Field(
        default=3, description='Seconds after which a timeout will be detected (default=3)')

    class Config:
        extra = pydantic.Extra.forbid


class GeneralSettings(BaseModel, ConfigMixin):
    wh_in_kwh: bool = Field(True, description='Automatically convert Wh to kWh', alias='Wh in kWh')
    republish_after: int = Field(
        120, description='Republish automatically after this time (if no other filter configured)',
        alias=REPUBLISH_ALIAS,
    )

    class Config:
        extra = pydantic.Extra.forbid


class Settings(BaseModel, AppConfigMixin):
    logging: LoggingSettings = LoggingSettings()
    mqtt: MqttConfig = MqttConfig()
    general: GeneralSettings = GeneralSettings()
    ports: List[PortSettings] = []
    devices: Dict[str, SmlDeviceConfig] = Field({}, description='Device configuration by ID or url',)

    class Config:
        extra = pydantic.Extra.forbid


def default_config() -> Settings:
    # File defaults
    s = Settings(
        ports=[PortSettings(url='COM1', timeout=3), PortSettings(url='/dev/ttyS0', timeout=3), ],
        devices={
            'DEVICE_ID_HEX': SmlDeviceConfig(
                mqtt=OptionalMqttPublishConfig(topic='DEVICE_BASE_TOPIC'),
                status=OptionalMqttPublishConfig(topic='status'),
                skip=['OBIS'],
                values={
                    'OBIS': SmlValueConfig(
                        mqtt=OptionalMqttPublishConfig(topic='OBIS'),
                        workarounds=[{'negative on energy meter status': True}],
                        transformations=[{'factor': 3}, {'offset': 100}, {'round': 2}],
                        filters=[{'diff': 10}, {'perc': 10}, {'every': 120}],
                    )
                }
            )
        }
    )
    return s


CONFIG = create_app_config(Settings(), default_config)
