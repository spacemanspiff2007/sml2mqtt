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
    async def create(cls, url: str, device: 'Device', timeout: float) -> 'SmlSerial':
        transport, protocol = await create_serial_connection(
            asyncio.get_event_loop(), cls, url, baudrate=9600)  # type: SerialTransport, SmlSerial

        protocol.url = url
        protocol.device = device
        protocol.timeout_secs = timeout
        return protocol

    def __init__(self) -> None:
        super().__init__()

        self.url: str = None
        self.device: 'Device' = None

        self.transport: typing.Optional[SerialTransport] = None

        self.timeout_secs: typing.Union[int, float] = 3
        self.timeout_event = asyncio.Event()
        self.timeout_task: typing.Optional[asyncio.Task] = None

        self.pause_task: typing.Optional[asyncio.Task] = None

        self.loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        self.transport = transport
        self.timeout_task = asyncio.create_task(self.watchdog())

        log.debug(f'Port {self.url} successfully opened')

        self.device.set_status(DeviceStatus.PORT_OPENED)

    def data_received(self, data: bytes):
        self.device.stream.add(data)
        self.timeout_event.set()

        self.pause_serial()
        asyncio.ensure_future(self.device.read(), loop=self.loop)

    async def resume_serial(self):
        await asyncio.sleep(0.4, loop=self.loop)

        self.pause_task = None
        self.transport.resume_reading()

    def pause_serial(self):
        self.transport.pause_reading()
        self.pause_task = asyncio.ensure_future(self.resume_serial(), loop=self.loop)

    def connection_lost(self, exc):
        self.close()

        log.info(f'Port {self.url} was closed')
        self.device.set_status(DeviceStatus.PORT_CLOSED)

    def close(self):
        if self.timeout_task is not None:
            self.timeout_task.cancel()
            self.timeout_task = None

        if self.pause_task is not None:
            self.pause_task.cancel()
            self.pause_task = None

        if not self.transport.is_closing():
            self.transport.close()

        self.device.stream.clear()

    async def watchdog(self):
        await asyncio.sleep(0.1)

        while True:
            self.timeout_event.clear()

            try:
                await asyncio.wait_for(self.timeout_event.wait(), self.timeout_secs)
                timeout = False
            except asyncio.TimeoutError:
                timeout = True

            if timeout:
                if self.device.status != DeviceStatus.MSG_TIMEOUT:
                    self.device.stream.clear()
                    log.warning(f'Timeout reading from {self.url}')
                    self.device.set_status(DeviceStatus.MSG_TIMEOUT)
