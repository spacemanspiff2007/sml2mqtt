from typing import Union

from easyconfig import AppBaseModel, BaseModel, create_app_config
from pydantic import Field

from .device import SmlDeviceConfig, SmlValueConfig
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig
from .source import HttpSourceSettings, SerialSourceSettings
from .types import LowerStr, ObisHex


class GeneralSettings(BaseModel):
    wh_in_kwh: bool = Field(
        True, description='Automatically convert Wh to kWh', alias='Wh in kWh'
    )
    republish_after: int = Field(
        120, description='Republish automatically after this time (if no other filter configured)',
        alias='republish after',
    )
    report_blank_energy_meters: bool = Field(
        False, description='Report blank energy meters (where the value is 0kwh)',
        alias='report blank energy meters', in_file=False
    )
    report_device_id: bool = Field(
        False, description='Report the device id even though it does never change',
        alias='report device id', in_file=False
    )
    device_id_obis: list[ObisHex] = Field(
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
    inputs: list[HttpSourceSettings | SerialSourceSettings] = []
    devices: dict[LowerStr, SmlDeviceConfig] = Field({}, description='Device configuration by ID or url',)


def default_config() -> Settings:
    # File defaults
    s = Settings(
        inputs=[SerialSourceSettings(url='COM1', timeout=3), SerialSourceSettings(url='/dev/ttyS0', timeout=3), ],
        devices={
            'DEVICE_ID_HEX': SmlDeviceConfig(
                mqtt=OptionalMqttPublishConfig(topic='DEVICE_BASE_TOPIC'),
                status=OptionalMqttPublishConfig(topic='status'),
                skip=['00112233445566'],
                values=[
                    SmlValueConfig(
                        obis='00112233445566',
                        mqtt=OptionalMqttPublishConfig(topic='OBIS'),
                        operations=[
                            {'negative on energy meter status': True},
                            {'factor': 3}, {'offset': 100}, {'round': 2},
                            # {'or': [
                            #     {'delta': 10},
                            #     {'delta': '10%'},
                            #     {'heartbeat': 120}
                            # ]}
                        ]
                    )
                ]
            )
        }
    )
    return s


CONFIG: Settings = create_app_config(Settings(), default_config)
