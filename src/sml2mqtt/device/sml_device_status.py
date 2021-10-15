from enum import Enum


class DeviceStatus(str, Enum):
    STARTUP = 'STARTUP'
    SHUTDOWN = 'SHUTDOWN'
    PORT_OPENED = 'PORT_OPENED'
    PORT_CLOSED = 'PORT_CLOSED'
    MSG_TIMEOUT = 'MSG_TIMEOUT'
    CRC_ERROR = 'CRC_ERROR'
    ERROR = 'ERROR'
    OK = 'OK'

    def is_shutdown_status(self) -> bool:
        return self.value in (DeviceStatus.PORT_CLOSED, DeviceStatus.ERROR, DeviceStatus.SHUTDOWN)
