from easyconfig import ConfigModel
from pydantic import conint, constr, Field, StrictBool, validator

QOS = conint(ge=0, le=2)
TOPIC_STR = constr(strip_whitespace=True, min_length=1)
STRIPPED_STR = constr(strip_whitespace=True)


class MqttPublishConfig(ConfigModel):
    topic: TOPIC_STR = 'sml2mqtt'
    qos: QOS = 0
    retain: StrictBool = False


class OptionalMqttPublishConfig(ConfigModel):
    topic: TOPIC_STR = None
    full_topic: TOPIC_STR = Field(None, alias='full topic')
    qos: QOS = None
    retain: StrictBool = None

    @validator('topic', 'full_topic')
    def validate_topic(cls, value):
        if value is None:
            return None

        if value.endswith('/'):
            raise ValueError('Topic must not end with "/"')
        if value.startswith('/'):
            raise ValueError('Topic must not start with "/"')
        return value

    @validator('full_topic')
    def check_full_or_partial(cls, v, values):
        if v is None:
            return None

        if values.get('topic') is not None:
            raise ValueError('Topic and full_topic can not be used at the same time!')
        return v


class MqttConnection(ConfigModel):
    client_id: STRIPPED_STR = Field('sml2mqtt', alias='client id')
    host: STRIPPED_STR = 'localhost'
    port: conint(gt=0) = 1833
    user: STRIPPED_STR = ''
    password: STRIPPED_STR = ''
    tls: StrictBool = False
    tls_insecure: StrictBool = Field(False, alias='tls insecure')


class MqttConfig(ConfigModel):
    connection: MqttConnection = MqttConnection()
    base: MqttPublishConfig = MqttPublishConfig()
    last_will: OptionalMqttPublishConfig = Field(
        default_factory=lambda: OptionalMqttPublishConfig(topic='status'), alias='last will')
