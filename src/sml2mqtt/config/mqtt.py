import random
import string

from easyconfig import BaseModel
from pydantic import Field, StrictBool, field_validator, model_validator

from sml2mqtt.config.mqtt_tls import MqttTlsOptions
from sml2mqtt.config.types import MqttQosInt, MqttTopicStr, StrippedStr


class MqttDefaultPublishConfig(BaseModel):
    qos: MqttQosInt = Field(
        0, description='Default value for QoS if no other QoS value in the config entry is set')
    retain: StrictBool = Field(
        False, description='Default value for retain if no other retain value in the config entry is set')


class OptionalMqttPublishConfig(BaseModel):
    topic: MqttTopicStr | None = Field(
        None, description='Topic fragment for building this topic with the parent topic')
    full_topic: MqttTopicStr | None = Field(
        None, alias='full topic', description='Full topic - will ignore the parent topic parts')
    qos: MqttQosInt | None = Field(
        None, description='QoS for publishing this value (if set - otherwise use parent)')
    retain: StrictBool | None = Field(
        None, description='Retain for publishing this value (if set - otherwise use parent)')

    @field_validator('topic', 'full_topic')
    def validate_topic(cls, value):
        if value is None:
            return None

        if value.endswith('/'):
            msg = 'Topic must not end with "/"'
            raise ValueError(msg)
        if value.startswith('/'):
            msg = 'Topic must not start with "/"'
            raise ValueError(msg)
        return value

    @model_validator(mode='after')
    def check_full_or_partial(self):
        if self.topic is not None and self.full_topic is not None:
            msg = 'Topic and full_topic can not be used at the same time!'
            raise ValueError(msg)
        return self


class MqttConnection(BaseModel):
    identifier: StrippedStr = Field('sml2mqtt-' + ''.join(random.choices(string.ascii_letters, k=13)),)
    host: StrippedStr = 'localhost'
    port: int = Field(1883, ge=0)
    user: StrippedStr = ''
    password: StrippedStr = ''

    tls: MqttTlsOptions | None = Field(None)


class MqttConfig(BaseModel):
    connection: MqttConnection = Field(
        default_factory=MqttConnection)
    topic: StrippedStr = Field(
        'sml2mqtt', alias='topic prefix', description='Prefix for all topics. Set to empty string to disable')
    defaults: MqttDefaultPublishConfig = Field(
        default_factory=MqttDefaultPublishConfig)
    last_will: OptionalMqttPublishConfig = Field(
        default_factory=lambda: OptionalMqttPublishConfig(topic='status'), alias='last will')
