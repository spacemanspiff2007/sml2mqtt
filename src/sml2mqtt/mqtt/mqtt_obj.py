import dataclasses
from collections.abc import Callable
from typing import Any, Final

from sml2mqtt.__log__ import get_logger
from sml2mqtt.config import OptionalMqttPublishConfig
from sml2mqtt.mqtt import publish

from .errors import MqttConfigValuesMissingError, TopicFragmentExpectedError


pub_func: Callable[[str, int | float | str, int, bool], Any] = publish


def publish_analyze(topic: str, value: int | float | str, qos: int, retain: bool):
    get_logger('mqtt.pub').info(f'{topic}: {value} (QOS: {qos}, retain: {retain})')


def patch_analyze():
    global pub_func

    pub_func = publish_analyze


@dataclasses.dataclass
class MqttCfg:
    topic_full: str | None = None
    topic_fragment: str | None = None
    qos: int | None = None
    retain: bool | None = None

    def set_config(self, config: OptionalMqttPublishConfig):
        self.topic_full = config.full_topic
        self.topic_fragment = config.topic
        self.qos = config.qos
        self.retain = config.retain


class MqttObj:
    def __init__(self, topic_fragment: str | None = None, qos: int | None = None, retain: bool | None = None):

        # Configured parts
        self.cfg = MqttCfg(topic_fragment=topic_fragment, qos=qos, retain=retain)

        # Effective config
        self.qos: int = 0
        self.retain: bool = False
        self.topic: str = ''

        self.parent: MqttObj | None = None
        self.children: list[MqttObj] = []

    def publish(self, value: str | int | float):
        pub_func(self.topic, value, self.qos, self.retain)

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

    def set_topic(self, topic: str | None) -> 'MqttObj':
        self.cfg.topic_fragment = topic
        self.update()
        return self

    def set_config(self, cfg: OptionalMqttPublishConfig | None) -> 'MqttObj':
        if cfg is None:
            return self

        self.cfg.set_config(cfg)
        self.update()
        return self

    def create_child(self, topic_fragment: str | None = None, qos: int | None = None,
                     retain: bool | None = None) -> 'MqttObj':
        child = self.__class__(topic_fragment=topic_fragment, qos=qos, retain=retain)
        child.parent = self
        self.children.append(child)
        child.update()
        return child


BASE_TOPIC: Final = MqttObj()


def setup_base_topic(topic: str, qos: int, retain: bool):
    BASE_TOPIC.cfg.topic_fragment = topic
    BASE_TOPIC.cfg.qos = qos
    BASE_TOPIC.cfg.retain = retain
    BASE_TOPIC.update()
