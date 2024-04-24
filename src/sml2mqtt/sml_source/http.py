from __future__ import annotations

from asyncio import TimeoutError, sleep
from typing import TYPE_CHECKING, Final

from aiohttp import BasicAuth, ClientError, ClientSession, ClientTimeout

from sml2mqtt.__log__ import get_logger
from sml2mqtt.const import DeviceTask
from sml2mqtt.errors import HttpStatusError
from sml2mqtt.runtime import on_shutdown


if TYPE_CHECKING:
    from sml2mqtt.config.inputs import HttpSourceSettings
    from sml2mqtt.const import DeviceProto


log = get_logger('http')

SESSION: ClientSession | None = None


async def get_session() -> ClientSession:
    global SESSION

    if SESSION is not None:
        return SESSION

    SESSION = ClientSession()
    on_shutdown(close_session, 'Close http session')
    return SESSION


async def close_session():
    global SESSION

    if (session := SESSION) is None:
        return None

    SESSION = None
    await session.close()

    # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
    await sleep(0.250)


class HttpSource:

    @classmethod
    async def create(cls, device: DeviceProto, settings: HttpSourceSettings):
        auth = None
        if settings.user or settings.password:
            auth = BasicAuth(settings.user, settings.password)

        return cls(device, str(settings.url), settings.interval, auth, timeout=settings.get_request_timeout())

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

    def start(self) -> None:
        self._task.start()

    async def cancel_and_wait(self) -> bool:
        return await self._task.cancel_and_wait()

    async def _http_task(self) -> None:
        log.debug(f'Requesting data from {self.url}')

        try:
            session = await get_session()
        except Exception as e:
            self.device.on_source_failed(f'Could not create client session: {e}')
            return None

        interval: float = self.interval
        com_errors: int = 0

        while True:
            await sleep(interval)
            interval = self.interval

            try:
                resp = await session.get(self.url, auth=self.auth, timeout=self.timeout)
                if resp.status != 200:
                    raise HttpStatusError(resp.status)  # noqa: TRY301

                payload = await resp.read()
                com_errors = 0
            except Exception as e:
                if isinstance(e, (ClientError, HttpStatusError, TimeoutError)):
                    com_errors += 1
                    max_ignore: int = 7
                    if com_errors <= max_ignore:
                        # errors:   1,   2,   3,   4,   5,   6,    7,    8,    9, ...
                        # factor: 0.4, 0.9, 1.9, 3.4, 5.4, 7.9, 10.9, 14.4, 18.4, ...
                        interval = (((com_errors - 0.5) ** 2) / 4 + 0.3) * self.interval
                        log.debug(f'Ignored {com_errors:d}/{max_ignore:d} {e} ({type(e)})')
                        continue

                self.device.on_error(e, show_traceback=False)
                continue

            self.device.on_source_data(payload)
