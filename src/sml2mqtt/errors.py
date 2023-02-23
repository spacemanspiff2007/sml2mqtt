class Sml2MqttException(Exception):     # noqa: N818
    pass


class DeviceSetupFailedError(Sml2MqttException):
    pass


class AllDevicesFailedError(Sml2MqttException):
    pass


# ------------------------------------------------------------------------------------
# Config mapping errors
# ------------------------------------------------------------------------------------
class Sml2MqttConfigMappingError(Sml2MqttException):
    pass


class ObisIdForConfigurationMappingNotFoundError(Sml2MqttConfigMappingError):
    pass
