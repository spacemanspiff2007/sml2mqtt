import asyncio
import typing
import logging

from serial_asyncio import SerialTransport, create_serial_connection
from .sml_device_status import DeviceStatus

if typing.TYPE_CHECKING:
    from .sml_device import Device


log = logging.getLogger('sml.serial')


class SmlSerial(asyncio.Protocol):
    @classmethod
    async def create(cls, url: str, device: 'Device') -> 'SmlSerial':
        transport, protocol = await create_serial_connection(
            asyncio.get_event_loop(), cls, url, baudrate=9600)  # type: SerialTransport, SmlSerial

        protocol.url = url
        protocol.device = device
        return protocol

    def __init__(self) -> None:
        super().__init__()

        self.url: str = None
        self.device: 'Device' = None

        self.transport: typing.Optional[SerialTransport] = None

        self.timeout = asyncio.Event()
        self.timeout_task: typing.Optional[asyncio.Task] = None

    def connection_made(self, transport):
        self.transport = transport
        self.timeout_task = asyncio.create_task(self.watchdog())

        log.debug(f'Port {self.url} successfully opened')

        self.device.set_status(DeviceStatus.PORT_OPENED)

    def data_received(self, data):
        self.device.stream.add(data)
        self.timeout.set()

    def connection_lost(self, exc):
        self.close()

        log.info(f'Port {self.url} was closed')
        self.device.set_status(DeviceStatus.PORT_CLOSED)

    def close(self):
        if self.timeout_task is None:
            return None

        self.timeout_task.cancel()
        self.timeout_task = None

        if not self.transport.is_closing():
            self.transport.close()

        self.device.stream.clear()

    async def watchdog(self):
        while True:
            await asyncio.sleep(0.1)
            self.timeout.clear()

            try:
                await asyncio.wait_for(self.timeout.wait(), 3)
                timeout = False
            except asyncio.TimeoutError:
                timeout = True

            if timeout:
                if self.device.status != DeviceStatus.MSG_TIMEOUT:
                    self.device.stream.clear()
                    log.warning(f'Timeout reading from {self.url}')
                    self.device.set_status(DeviceStatus.MSG_TIMEOUT)
