from easyconfig import AppBaseModel, BaseModel, create_app_config
from pydantic import Field

from .device import SmlDeviceConfig, SmlValueConfig
from .inputs import HttpSourceSettings, SerialSourceSettings
from .logging import LoggingSettings
from .mqtt import MqttConfig, OptionalMqttPublishConfig
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
    crc: list[str] = Field(
        default=['x25', 'kermit'],
        description='Which crc algorithms are used to calculate the checksum of the smart meter',
        alias='crc', in_file=False
    )


class Settings(AppBaseModel):
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    inputs: list[HttpSourceSettings | SerialSourceSettings] = Field(default_factory=list, discriminator='type')
    devices: dict[LowerStr, SmlDeviceConfig] = Field({}, description='Device configuration by ID or url',)


def default_config() -> Settings:
    # File defaults
    return Settings(
        inputs=[SerialSourceSettings(type='serial', url='COM1', timeout=6),
                SerialSourceSettings(type='serial', url='/dev/ttyS0', timeout=6), ],
        devices={
            'device_id_hex': SmlDeviceConfig(
                mqtt=OptionalMqttPublishConfig(topic='DEVICE_BASE_TOPIC'),
                status=OptionalMqttPublishConfig(topic='status'),
                skip={'00112233445566'},
                values=[
                    SmlValueConfig(
                        obis='00112233445566',
                        mqtt=OptionalMqttPublishConfig(topic='OBIS'),
                        operations=[
                            {'negative on energy meter status': True},
                            {'factor': 3}, {'offset': 100}, {'round': 2},
                            {'type': 'change filter'},
                            {'refresh action': 600}
                        ]
                    )
                ]
            )
        }
    )


CONFIG: Settings = create_app_config(Settings(), default_config)
