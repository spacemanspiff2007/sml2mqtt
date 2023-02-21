import asyncio
from asyncio import create_task, Task
from typing import Awaitable, Callable, Final, Optional, TYPE_CHECKING

from serial_asyncio import create_serial_connection, SerialTransport

from sml2mqtt.__log__ import get_logger
from sml2mqtt.config.config import PortSettings
from sml2mqtt.device import DeviceStatus

if TYPE_CHECKING:
    import sml2mqtt


log = get_logger('serial')


class SmlSerial(asyncio.Protocol):
    @classmethod
    async def create(cls, settings: PortSettings, device: 'sml2mqtt.device_id.Device') -> 'SmlSerial':
        transport, protocol = await create_serial_connection(
            asyncio.get_event_loop(), cls,
            url=settings.url,
            baudrate=settings.baudrate, parity=settings.parity,
            stopbits=settings.stopbits, bytesize=settings.bytesize)  # type: SerialTransport, SmlSerial

        protocol.url = settings.url
        protocol.device = device
        return protocol

    def __init__(self) -> None:
        super().__init__()

        self.url: Optional[str] = None
        self.device: Optional['sml2mqtt.device_id.Device'] = None

        self.transport: Optional[SerialTransport] = None

        self._task: Optional[Task] = None

        self.on_data_cb: Final = Callable[[bytes], Awaitable]

    def connection_made(self, transport):
        self.transport = transport
        log.debug(f'Port {self.url} successfully opened')

        self.device.set_status(DeviceStatus.PORT_OPENED)

    def connection_lost(self, exc):
        self.close()

        log.info(f'Port {self.url} was closed')
        self.device.set_status(DeviceStatus.PORT_CLOSED)

    def data_received(self, data: bytes):
        self.transport.pause_reading()
        create_task(self.device.serial_data_read(data))

    async def _chunk_task(self):
        while True:
            await asyncio.sleep(0.1)
            self.transport.resume_reading()

    def start(self):
        assert self._task is None
        self._task = create_task(self._chunk_task(), name=f'Chunk task {self.url:s}')

    def close(self):
        if not self.transport.is_closing():
            self.transport.close()

        task = self._task
        self._task = None

        task.cancel()
        return task

    async def shutdown(self):
        await self.close()
