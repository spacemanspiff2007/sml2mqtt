from typing import Dict, List, Union

from easyconfig import AppBaseModel, BaseModel, create_app_config
from pydantic import Field, StrictStr

from .device import REPUBLISH_ALIAS, SmlDeviceConfig, SmlValueConfig
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig
from .source import HttpSourceSettings, PortSourceSettings


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
    device_id_obis: List[StrictStr] = Field(
        # 0100000009ff (1-0:0.0.9*255) : Geräteeinzelidentifikation
        # 0100600100ff (1-0:96.1.0*255): Produktionsnummer
        ['0100000009ff', '0100600100ff'],
        description='Additional OBIS fields for the serial number to configuration matching',
        alias='device id obis', in_file=False
    )


class Settings(AppBaseModel):
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    ports: List[Union[HttpSourceSettings, PortSourceSettings]] = []
    devices: Dict[str, SmlDeviceConfig] = Field({}, description='Device configuration by ID or url',)


def default_config() -> Settings:
    # File defaults
    s = Settings(
        ports=[PortSourceSettings(url='COM1', timeout=3), PortSourceSettings(url='/dev/ttyS0', timeout=3), ],
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


CONFIG: Settings = create_app_config(Settings(), default_config)
