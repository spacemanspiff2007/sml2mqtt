class Sml2MqttException(Exception):
    pass


class DeviceSetupFailed(Sml2MqttException):
    pass


class AllDevicesFailed(Sml2MqttException):
    pass
