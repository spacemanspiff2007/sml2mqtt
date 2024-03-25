import random
import string

from easyconfig import BaseModel
from pydantic import Field, StrictBool, conint, constr, field_validator, model_validator


QOS = conint(ge=0, le=2)
TOPIC_STR = constr(strip_whitespace=True, min_length=1)
STRIPPED_STR = constr(strip_whitespace=True)


class MqttDefaultPublishConfig(BaseModel):
    qos: QOS = Field(
        0, description='Default value for QOS if no other QOS value in the config entry is set')
    retain: StrictBool = Field(
        False, description='Default value for retain if no other retain value in the config entry is set')


class OptionalMqttPublishConfig(BaseModel):
    topic: TOPIC_STR | None = Field(None, description='Topic fragment for building this topic with the parent topic')
    full_topic: TOPIC_STR | None = Field(
        None, alias='full topic', description='Full topic - will ignore the parent topic parts')
    qos: QOS | None = Field(None, description='QoS for publishing this value (if set - otherwise use parent)')
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
    identifier: STRIPPED_STR = Field('sml2mqtt-' + ''.join(random.choices(string.ascii_letters, k=13)),)
    host: STRIPPED_STR = 'localhost'
    port: conint(gt=0) = 1883
    user: STRIPPED_STR = ''
    password: STRIPPED_STR = ''
    tls: StrictBool = False
    tls_insecure: StrictBool = Field(False, alias='tls insecure')


class MqttConfig(BaseModel):
    connection: MqttConnection = Field(default_factory=MqttConnection)
    topic: TOPIC_STR = Field('sml2mqtt', alias='topic prefix')
    defaults: MqttDefaultPublishConfig = Field(default_factory=MqttDefaultPublishConfig)
    last_will: OptionalMqttPublishConfig = Field(
        default_factory=lambda: OptionalMqttPublishConfig(topic='status'), alias='last will')
