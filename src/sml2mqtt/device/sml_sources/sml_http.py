from asyncio import CancelledError, create_task, sleep, Task
from typing import Final, Optional, TYPE_CHECKING

from aiohttp import BasicAuth, ClientSession, ClientTimeout

from sml2mqtt.__log__ import get_logger
from sml2mqtt.config.config import HttpSourceSettings
from sml2mqtt.device import DeviceStatus

from .base import SmlSourceBase

if TYPE_CHECKING:
    import sml2mqtt


log = get_logger('http')


class HttpSource(SmlSourceBase):

    @classmethod
    async def create(cls, settings: HttpSourceSettings, device: 'sml2mqtt.device.Device') -> 'HttpSource':
        auth = None
        if settings.user or settings.password:
            auth = BasicAuth(settings.user, settings.password)

        return cls(device, str(settings.url), settings.interval, auth, timeout=ClientTimeout(settings.timeout / 2))

    def __init__(self, device: 'sml2mqtt.device.Device',
                 url: str, interval: float, auth: Optional['BasicAuth'], timeout: 'ClientTimeout') -> None:
        super().__init__()
        self.device: Final = device

        self.url: Final = url
        self.auth: Final = auth
        self.timeout: Final = timeout

        self.interval = interval
        self.task: Optional[Task] = None

    async def start(self):
        assert self.task is None
        self.task = create_task(self._http_task(), name=f'Http task {self.url:s}')

    async def stop(self):
        if (task := self.task) is None:
            return None

        task.cancel()
        self.task = None

    async def _http_task(self):
        self.device.set_status(DeviceStatus.STARTUP)
        log.debug(f'Requesting data from {self.url}')

        async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
            while True:
                await sleep(self.interval)

                try:
                    resp = await session.get(self.url)
                    if resp.status >= 400:
                        log.error(resp)
                        self.device.set_status(DeviceStatus.ERROR)
                        continue

                    payload = await resp.read()
                except Exception as e:
                    log.error(e)
                    self.device.set_status(DeviceStatus.ERROR)
                    continue

                self.device.serial_data_read(payload)

    async def wait_for_stop(self):
        if self.task is None:
            return False
        try:
            await self.task
        except CancelledError:
            pass
        return True
