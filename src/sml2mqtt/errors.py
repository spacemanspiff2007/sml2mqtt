from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

if TYPE_CHECKING:
    from logging import Logger
    from smllib.sml import SmlListEntry


class Sml2MqttException(Exception):
    pass


class Sml2MqttExceptionWithLog(Sml2MqttException):
    def log_msg(self, log: Logger):
        raise NotImplementedError()


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


# ------------------------------------------------------------------------------------
# Value Processing Errors
# ------------------------------------------------------------------------------------

class UnprocessedObisValuesReceivedError(Sml2MqttExceptionWithLog):
    def __init__(self, *values: SmlListEntry):
        super().__init__()
        self.values: Final = values

    @override
    def log_msg(self, log: Logger):
        log.error(f'Unexpected obis id{"" if len(self.values) == 1 else "s"} received!')
        for value in self.values:
            for line in value.format_msg().splitlines():
                log.error(line)


class RequiredObisValueNotInFrameError(Sml2MqttExceptionWithLog):
    def __init__(self, *obis: str):
        super().__init__()
        self.obis: Final = obis

    @override
    def log_msg(self, log: Logger):
        log.error(f'Expected obis id{"" if len(self.obis) == 1 else "s"} missing in frame: {", ".join(self.obis)}!')
