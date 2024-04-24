from enum import Enum


class DeviceStatus(str, Enum):
    STARTUP = 'STARTUP'
    SHUTDOWN = 'SHUTDOWN'

    SOURCE_FAILED = 'SOURCE_FAILED'
    MSG_TIMEOUT = 'MESSAGE_TIMEOUT'
    CRC_ERROR = 'CRC_ERROR'
    ERROR = 'ERROR'

    OK = 'OK'

    def is_shutdown_status(self) -> bool:
        return self.value in (DeviceStatus.ERROR, DeviceStatus.SOURCE_FAILED, DeviceStatus.SHUTDOWN)

    def __str__(self) -> str:
        return self.value
