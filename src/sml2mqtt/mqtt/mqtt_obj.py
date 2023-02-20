import dataclasses
from asyncio import create_task
from typing import Final, List, Optional, Union

from sml2mqtt import CMD_ARGS
from sml2mqtt.__log__ import get_logger
from sml2mqtt.config import OptionalMqttPublishConfig
from sml2mqtt.mqtt import publish

from .errors import MqttConfigValuesMissingError, TopicFragmentExpectedError


@dataclasses.dataclass
class MqttCfg:
    topic_full: Optional[str] = None
    topic_fragment: Optional[str] = None
    qos: Optional[int] = None
    retain: Optional[bool] = None

    def set_config(self, config: Optional[OptionalMqttPublishConfig]):
        self.topic_full = config.full_topic
        self.topic_fragment = config.topic
        self.qos = config.qos
        self.retain = config.retain


class MqttObj:
    def __init__(self, topic_fragment: Optional[str] = None, qos: Optional[int] = None, retain: Optional[bool] = None):

        # Configured parts
        self.cfg = MqttCfg(topic_fragment=topic_fragment, qos=qos, retain=retain)

        # Effective config
        self.qos: int = 0
        self.retain: bool = False
        self.topic: str = ''

        self.parent: Optional[MqttObj] = None
        self.children: List[MqttObj] = []

    def publish(self, value: Union[str, int, float, bytes]):
        # do not publish when the analyze flag is set
        if CMD_ARGS.analyze:
            get_logger('mqtt.pub').info(f'{self.topic}: {value} (QOS: {self.qos}, retain: {self.retain})')
        else:
            create_task(publish(self.topic, value, self.qos, self.retain))

    def update(self) -> 'MqttObj':
        self._merge_values()
        for c in self.children:
            c.update()
        return self

    def _merge_values(self) -> 'MqttObj':

        # no parent -> just set the config
        if self.parent is None:
            assert self.cfg.topic_full is None
            self.topic = self.cfg.topic_fragment    # expect fragment only
            self.qos = self.cfg.qos
            self.retain = self.cfg.retain
            if self.topic is None or self.qos is None or self.retain is None:
                raise MqttConfigValuesMissingError()
            return self

        # effective topic
        if self.cfg.topic_full:
            self.topic = self.cfg.topic_full
        else:
            if not self.cfg.topic_fragment:
                raise TopicFragmentExpectedError()
            self.topic = f'{self.parent.topic}/{self.cfg.topic_fragment}'

        # effective QOS
        self.qos = self.cfg.qos
        if self.qos is None:
            self.qos = self.parent.qos

        # effective retain
        self.retain = self.cfg.retain
        if self.retain is None:
            self.retain = self.parent.retain
        return self

    def set_topic(self, topic: str) -> 'MqttObj':
        self.cfg.topic_fragment = topic
        self.update()
        return self

    def set_config(self, cfg: Optional[OptionalMqttPublishConfig]) -> 'MqttObj':
        if cfg is None:
            return self

        self.cfg.set_config(cfg)
        self.update()
        return self

    def create_child(self, topic_fragment: Optional[str] = None, qos: Optional[int] = None,
                     retain: Optional[bool] = None) -> 'MqttObj':
        child = self.__class__(topic_fragment=topic_fragment, qos=qos, retain=retain)
        child.parent = self
        self.children.append(child)
        child.update()
        return child


BASE_TOPIC: Final = MqttObj()
