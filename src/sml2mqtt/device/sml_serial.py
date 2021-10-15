import asyncio
from asyncio import create_task, Task
from typing import Awaitable, Callable, Final, Optional, TYPE_CHECKING

from serial_asyncio import create_serial_connection, SerialTransport

from sml2mqtt.__log__ import get_logger
from sml2mqtt.device import DeviceStatus

if TYPE_CHECKING:
    import sml2mqtt


log = get_logger('serial')


class SmlSerial(asyncio.Protocol):
    @classmethod
    async def create(cls, url: str, device: 'sml2mqtt.device_id.Device') -> 'SmlSerial':
        transport, protocol = await create_serial_connection(
            asyncio.get_event_loop(), cls, url, baudrate=9600)  # type: SerialTransport, SmlSerial

        protocol.url = url
        protocol.device = device
        return protocol

    def __init__(self) -> None:
        super().__init__()

        self.url: Optional[str] = None
        self.device: Optional['sml2mqtt.device_id.Device'] = None

        self.transport: Optional[SerialTransport] = None

        self.pause_task: Optional[Task] = None

        self.on_data_cb: Final = Callable[[bytes], Awaitable]

    def connection_made(self, transport):
        self.transport = transport
        log.debug(f'Port {self.url} successfully opened')

        self.device.set_status(DeviceStatus.PORT_OPENED)

    def data_received(self, data: bytes):
        self.pause_serial()
        create_task(self.device.serial_data_read(data))

    async def resume_serial(self):
        try:
            await asyncio.sleep(0.4)
            self.transport.resume_reading()
        finally:
            self.pause_task = None

    def pause_serial(self):
        self.transport.pause_reading()
        self.pause_task = create_task(self.resume_serial())

    def connection_lost(self, exc):
        self.close()

        log.info(f'Port {self.url} was closed')
        self.device.set_status(DeviceStatus.PORT_CLOSED)

    def close(self):
        if self.pause_task is not None:
            self.pause_task.cancel()
            self.pause_task = None

        if not self.transport.is_closing():
            self.transport.close()
