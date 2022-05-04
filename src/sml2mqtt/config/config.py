from typing import Dict, List, Union

from easyconfig import AppBaseModel, BaseModel, create_app_config
from pydantic import constr, Field

from .device import REPUBLISH_ALIAS, SmlDeviceConfig, SmlValueConfig
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig


class PortSettings(BaseModel):
    url: constr(strip_whitespace=True, min_length=1, strict=True) = Field(..., description='Device path')
    timeout: Union[int, float] = Field(
        default=3, description='Seconds after which a timeout will be detected (default=3)')


class GeneralSettings(BaseModel):
    wh_in_kwh: bool = Field(True, description='Automatically convert Wh to kWh', alias='Wh in kWh')
    republish_after: int = Field(
        120, description='Republish automatically after this time (if no other filter configured)',
        alias=REPUBLISH_ALIAS,
    )
    report_blank_energy_meters: bool = Field(
        False, description='Report blank energy meters (where the value is 0kwh)',
        alias='report blank energy meters', in_file=False
    )
    report_device_id: bool = Field(
        False, description='Report the device id even though it does never change',
        alias='report device id', in_file=False
    )


class Settings(AppBaseModel):
    logging: LoggingSettings = LoggingSettings()
    mqtt: MqttConfig = MqttConfig()
    general: GeneralSettings = GeneralSettings()
    ports: List[PortSettings] = []
    devices: Dict[str, SmlDeviceConfig] = Field({}, description='Device configuration by ID or url',)


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
