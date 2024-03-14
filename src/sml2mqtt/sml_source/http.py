from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING, Final

from aiohttp import BasicAuth, ClientSession, ClientTimeout

from sml2mqtt.__log__ import get_logger
from sml2mqtt.const import DeviceTask
from sml2mqtt.errors import HttpStatusError


if TYPE_CHECKING:
    from sml2mqtt.config.source import HttpSourceSettings
    from sml2mqtt.const import DeviceProto


log = get_logger('http')

SESSION: ClientSession | None = None
SESSION_CTR: int = 0


async def get_session() -> ClientSession:
    global SESSION, SESSION_CTR

    if SESSION is not None:
        SESSION_CTR += 1
        return SESSION

    SESSION = ClientSession()
    SESSION_CTR += 1
    return SESSION


async def close_session():
    global SESSION, SESSION_CTR

    SESSION_CTR -= 1
    if SESSION_CTR > 0:
        return None

    SESSION_CTR = 0

    if (session := SESSION) is not None:
        SESSION = None
        await session.close()


class HttpSource:

    @classmethod
    async def create(cls, device: DeviceProto, settings: HttpSourceSettings):
        auth = None
        if settings.user or settings.password:
            auth = BasicAuth(settings.user, settings.password)

        return cls(device, str(settings.url), settings.interval, auth, timeout=ClientTimeout(settings.timeout / 2))

    def __init__(self, device: DeviceProto,
                 url: str, interval: float,
                 auth: BasicAuth | None, timeout: ClientTimeout) -> None:
        super().__init__()
        self.device: Final = device

        self.url: Final = url
        self.auth: Final = auth
        self.timeout: Final = timeout

        self.interval = interval
        self._task: Final = DeviceTask(device, self._http_task, name=f'Http Task {self.device.name:s}')

    async def start(self):
        await self._task.start()

    async def stop(self):
        return await self._task.stop()

    async def _http_task(self):
        log.debug(f'Requesting data from {self.url}')

        try:
            session = await get_session()
        except Exception as e:
            self.device.on_source_failed(f'Could not create client session: {e}')
            return None

        try:
            while True:
                await sleep(self.interval)

                try:
                    resp = await session.get(self.url, auth=self.auth, timeout=self.timeout)
                    if resp.status != 200:
                        raise HttpStatusError(resp.status)  # noqa: TRY301

                    payload = await resp.read()
                except Exception as e:
                    self.device.on_error(e, show_traceback=False)
                    continue

                self.device.on_source_data(payload)
        finally:
            await close_session()
