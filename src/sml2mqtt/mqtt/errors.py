class MqttError(Exception):
    pass


class TopicFragmentExpectedError(Exception):
    pass


class MqttTopicEmpty(Exception):
    pass


class MqttConfigValuesMissingError(Exception):
    pass
