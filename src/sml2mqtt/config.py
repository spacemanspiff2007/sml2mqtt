import logging
from pathlib import Path
from typing import Dict, List

from EasyCo import ConfigContainer, ConfigEntry, ConfigFile
from voluptuous import Invalid, Range


class Connection(ConfigContainer):
    client_id: str = 'sml2mqtt'
    host: str = 'localhost'
    port: int = 1883
    user: str = ''
    password: str = ''
    tls: bool = False
    tls_insecure: bool = False


class Topics(ConfigContainer):
    base_topic: str = ConfigEntry('sml2mqtt', key_name='base topic', description='Topic that will prefix all topics')
    last_will: str = ConfigEntry('status', key_name='last will', description='Last will topic')
    alias: Dict[str, str] = ConfigEntry(default_factory=lambda: {'0100010800ff': 'total_energy'}, validator={str: str},
                                        description='These aliases are replaced in the mqtt topics')

    def on_all_values_set(self):
        self.alias = {k: v.replace(' ', '_') for k, v in self.alias.items()}

    def get_topic(self, *args) -> str:
        args = [self.alias.get(a, a) for a in args]
        topic = self.base_topic + '/' + '/'.join(args)
        return topic.replace('//', '/')


class Publish(ConfigContainer):
    qos: int = ConfigEntry(default=0, description='Default QoS when publishing values')
    retain: bool = ConfigEntry(default=False, description='Default retain flag when publishing values')


class Mqtt(ConfigContainer):
    connection = Connection()
    topics = Topics()
    publish = Publish()


def log_lvl_validator(v, msg=''):
    if v not in logging._nameToLevel:
        raise Invalid(msg or f'Level must be one of {", ".join(logging._nameToLevel)}')

    return logging._nameToLevel[v]


class Logging(ConfigContainer):
    level: str = ConfigEntry(default='INFO', description='Verbosity level for the logfile',
                             validator=log_lvl_validator)
    file: Path = ConfigEntry(default_factory=lambda: str(CONFIG._path.with_name('sml2mqtt.log')),
                             description='Path to logfile')


class DeviceConfig:
    def __init__(self, device: str, timeout: float, skip: List[str]):
        self.device: str = device
        self.timeout: float = timeout
        self.skip: List[str] = skip

    @classmethod
    def create(cls, _in: dict, msg=None):
        if not isinstance(_in, dict) or not _in:
            raise Invalid(msg or 'Device config must be a dict')

        device = _in['device']
        if not isinstance(device, str) or not device:
            raise Invalid(msg or 'device must be a valid string')

        timeout = _in['timeout']
        if not isinstance(timeout, (float, int)) or timeout < 1:
            raise Invalid(msg or f'timeout must be a valid int/float and >= 1 ({type(timeout)}, {timeout})')

        skip = _in.get('skip', [])
        for i, v in enumerate(skip):
            if not isinstance(v, str) or not v:
                raise Invalid(msg or f'Skipped value at {i} must be a valid string')

        return cls(device, timeout, skip)


def device_validator(_in, msg=None):
    if not isinstance(_in, list):
        raise Invalid(msg or f'Devices must be a list (is {type(_in)})')
    return [DeviceConfig.create(e) for e in _in]


class General(ConfigContainer):
    max_wait: int = ConfigEntry(
        default=120, key_name='max wait', validator=Range(min=2),
        description='Time in seconds sml2mqtt waits for a value change until the value gets republished'
    )


class SmlMqttConfig(ConfigFile):
    mqtt = Mqtt()
    log = Logging()
    general = General()
    devices: List[DeviceConfig] = ConfigEntry(
        default_factory=lambda: [{'device': 'COM1', 'timeout': 3, 'skip': ['value ids that will', 'not be reported']},
                                 {'device': '/dev/ttyS0', 'timeout': 3}],
        description='Configuration of the sml devices', validator=device_validator)


CONFIG = SmlMqttConfig()
