import asyncio
from asyncio import CancelledError, create_task, Task
from time import monotonic
from typing import Optional, TYPE_CHECKING

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

        self.task: Optional[Task] = None
        self.last_read: Optional[float] = None

    def connection_made(self, transport: SerialTransport):
        self.transport = transport
        log.debug(f'Port {self.url} successfully opened')

        self.device.set_status(DeviceStatus.PORT_OPENED)

        # so we can read bigger chunks at once in case someone uses a higher baudrate
        self.transport._max_read_size = 10_240

    def connection_lost(self, exc):
        self.close()

        log.info(f'Port {self.url} was closed')
        self.device.set_status(DeviceStatus.PORT_CLOSED)

    def data_received(self, data: bytes):
        self.transport.pause_reading()
        self.last_read = monotonic()

        self.device.serial_data_read(data)

    async def _chunk_task(self):
        interval = 0.2

        while True:
            await asyncio.sleep(interval)

            if self.last_read is not None:
                diff_to_interval = interval - (monotonic() - self.last_read)
                self.last_read = None
                if diff_to_interval >= 0.001:
                    await asyncio.sleep(diff_to_interval)

            self.transport.resume_reading()

    def start(self):
        assert self.task is None
        self.task = create_task(self._chunk_task(), name=f'Chunk task {self.url:s}')

    def cancel(self):
        self.close()

    async def wait_for_cancel(self):
        if self.task is None:
            return False
        try:
            await self.task
        except CancelledError:
            pass
        return True

    def close(self):
        if not self.transport.is_closing():
            self.transport.close()

        if (task := self.task) is None:
            return None

        task.cancel()
        self.task = None
        return task
