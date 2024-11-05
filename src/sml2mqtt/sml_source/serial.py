from __future__ import annotations

import asyncio
import logging
from asyncio import Protocol
from time import monotonic
from typing import TYPE_CHECKING, Final

from serial_asyncio import SerialTransport, create_serial_connection

from sml2mqtt.__log__ import get_logger
from sml2mqtt.const import DeviceTask


if TYPE_CHECKING:
    from sml2mqtt.config.inputs import SerialSourceSettings
    from sml2mqtt.const import DeviceProto


log = get_logger('serial')


class SerialSource(Protocol):
    @classmethod
    async def create(cls, device: DeviceProto, settings: SerialSourceSettings) -> SerialSource:
        transport, protocol = await create_serial_connection(
            asyncio.get_event_loop(),
            lambda: cls(device, settings.url),
            url=settings.url,
            baudrate=settings.baudrate, parity=settings.parity,
            stopbits=settings.stopbits, bytesize=settings.bytesize
        )  # type: SerialTransport, SerialSource

        return protocol

    def __init__(self, device: DeviceProto, url: str) -> None:
        super().__init__()

        self.url: Final = url
        self.device: Final = device

        self.transport: SerialTransport | None = None

        self._task: Final = DeviceTask(device, self._chunk_task, name=f'Serial Task {self.device.name:s}')

        self.last_read: float | None = 0.0

    def start(self) -> None:
        self._task.start()

    async def cancel_and_wait(self):
        return await self._task.cancel_and_wait()

    def connection_made(self, transport: SerialTransport) -> None:
        self.transport = transport
        log.debug(f'Port {self.url:s} successfully opened')

        # so we can read bigger chunks at once in case someone uses a higher baudrate
        self.transport._max_read_size = 10_240

    def connection_lost(self, exc: Exception | None) -> None:

        lvl = logging.INFO
        ex_str = ''
        if exc is not None:
            ex_str = f': {exc}'
            lvl = logging.ERROR

        log.log(lvl, f'Port {self.url:s} was closed{ex_str:s}')
        self.device.on_source_failed(f'Connection to port {self.url:s} lost')

    def data_received(self, data: bytes) -> None:
        self.transport.pause_reading()

        self.last_read = monotonic()
        self.device.on_source_data(data)

    async def _chunk_task(self) -> None:
        interval = 0.2

        while True:
            await asyncio.sleep(interval)

            if self.last_read is not None:
                diff_to_interval = interval - (monotonic() - self.last_read)
                self.last_read = None
                if diff_to_interval >= 0.001:
                    await asyncio.sleep(diff_to_interval)

            # safe to be called multiple times in a row
            self.transport.resume_reading()
