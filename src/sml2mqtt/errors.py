class Sml2MqttException(Exception):     # noqa: N818
    pass


class AllDevicesFailedError(Sml2MqttException):
    pass


# ------------------------------------------------------------------------------------
# Initial setup failed
# ------------------------------------------------------------------------------------
class InitialSetupFailedError(Sml2MqttException):
    pass


class DeviceSetupFailedError(InitialSetupFailedError):
    pass


class InitialMqttConnectionFailedError(InitialSetupFailedError):
    pass


# ------------------------------------------------------------------------------------
# Config mapping errors
# ------------------------------------------------------------------------------------
class Sml2MqttConfigMappingError(Sml2MqttException):
    pass


class ObisIdForConfigurationMappingNotFoundError(Sml2MqttConfigMappingError):
    pass
