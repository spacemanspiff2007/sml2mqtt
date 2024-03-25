from easyconfig import BaseModel
from pydantic import Field

from .mqtt import OptionalMqttPublishConfig
from .operations import OperationsListType
from .types import ObisHex


class SmlValueConfig(BaseModel):
    obis: ObisHex = Field(description='Obis code for this value')
    mqtt: OptionalMqttPublishConfig | None = Field(
        default=None,
        description='Mqtt config for this value (optional)'
    )

    operations: OperationsListType = Field(
        default=[],
        alias='operations',
        description='A sequence of operations that will be evaluated one after another.\n'
                    'If one operation blocks this will return nothing.'
    )


class SmlDeviceConfig(BaseModel):
    """Configuration for a sml device"""

    mqtt: OptionalMqttPublishConfig | None = Field(None, description='Optional MQTT configuration for this meter.')

    status: OptionalMqttPublishConfig = Field(
        default=OptionalMqttPublishConfig(topic='status'),
        description='Optional MQTT status topic configuration for this meter'
    )

    skip: set[ObisHex] = Field(
        default_factory=set, description='OBIS codes (HEX) of values that will not be published (optional)')

    values: list[SmlValueConfig] = Field(
        default=[], description='Configurations for each of the values (optional)')
