import dataclasses
from asyncio import create_task
from typing import List, Optional, Union

from sml2mqtt import CMD_ARGS
from sml2mqtt.__log__ import get_logger
from sml2mqtt.config import OptionalMqttPublishConfig
from sml2mqtt.mqtt import publish


class TopicFragmentExpected(Exception):
    pass


class MqttConfigValuesMissing(Exception):
    pass


@dataclasses.dataclass
class MqttCfg:
    topic_full: Optional[str] = None
    topic_fragment: Optional[str] = None
    qos: Optional[int] = None
    retain: Optional[bool] = None

    def is_full_config(self) -> bool:
        if self.topic_fragment is None and self.topic_full is None:
            return False
        if self.qos is None:
            return False
        if self.retain is None:
            return False
        return True


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

        if self.parent is None:
            if not self.cfg.is_full_config():
                raise MqttConfigValuesMissing()

        if self.cfg.topic_full:
            self.topic = self.cfg.topic_full
        else:
            if not self.cfg.topic_fragment:
                raise TopicFragmentExpected()
            if self.parent is None:
                self.topic = self.cfg.topic_fragment
            else:
                self.topic = f'{self.parent.topic}/{self.cfg.topic_fragment}'

        self.qos = self.cfg.qos
        if self.qos is None:
            self.qos = self.parent.qos

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

        local = self.cfg
        local.topic_full = cfg.full_topic
        local.topic_fragment = cfg.topic
        local.qos = cfg.qos
        local.retain = cfg.retain
        self.update()
        return self

    def create_child(self, topic_fragment: Optional[str] = None, qos: Optional[int] = None,
                     retain: Optional[bool] = None) -> 'MqttObj':
        child = self.__class__(topic_fragment=topic_fragment, qos=qos, retain=retain)
        child.parent = self
        self.children.append(child)
        child.update()
        return child


BASE_TOPIC = MqttObj()
