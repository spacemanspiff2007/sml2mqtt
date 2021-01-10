import enum


class DeviceStatus(enum.Enum):
    STARTUP = enum.auto()
    SHUTDOWN = enum.auto()
    PORT_OPENED = enum.auto()
    PORT_CLOSED = enum.auto()
    MSG_TIMEOUT = enum.auto()
    CRC_ERROR = enum.auto()
    ERROR = enum.auto()
    OK = enum.auto()
