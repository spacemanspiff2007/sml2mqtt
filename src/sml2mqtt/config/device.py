from easyconfig import BaseModel
from pydantic import Field

from .mqtt import OptionalMqttPublishConfig
from .operations import OperationsListType
from .types import ObisHex


class SmlValueConfig(BaseModel):
    obis: ObisHex = Field(description='Obis code for this value')
    mqtt: OptionalMqttPublishConfig = Field(None, description='Mqtt config for this value (optional)')

    operations: OperationsListType = Field(
        alias='operations', description='A sequence of operations that will be evaluated one after another. '
                                        'As soon as one operation blocks a value the whole sequence will be aborted and'
                                        'nothing will be published for this frame.'
    )


class SmlDeviceConfig(BaseModel):
    """Configuration for a sml device"""

    mqtt: OptionalMqttPublishConfig | None = Field(None, description='Optional MQTT configuration for this meter.')

    status: OptionalMqttPublishConfig | None = Field(
        default=OptionalMqttPublishConfig(topic='status'),
        description='Optional MQTT status topic configuration for this meter'
    )

    skip: set[ObisHex] | None = Field(
        default=None, description='OBIS codes (HEX) of values that will not be published (optional)')

    values: list[SmlValueConfig] = Field(
        default=[], description='Configurations for each of the values (optional)')
