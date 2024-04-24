from asyncio import sleep
from collections.abc import Callable
from unittest.mock import Mock

from smllib import SmlStreamReader
from smllib.builder import CTX_HINT
from smllib.errors import CrcError
from typing_extensions import override

from sml2mqtt.const import EnhancedSmlFrame


async def wait_for_call(mock: Mock | Callable, timeout: float) -> Mock:
    mock.assert_not_called()

    interval = 0.01
    cycles = int(timeout / interval)

    while not mock.called:
        await sleep(interval)

        cycles -= 1
        if cycles <= 0:
            raise TimeoutError()

    return mock


class PatchedSmlStreamReader(SmlStreamReader):
    _CRC_ERROR = 'CRC_ERROR'

    @override
    def __init__(self, build_ctx: CTX_HINT | None = None):
        super().__init__(build_ctx)
        self.returns = []

    def add(self, _bytes: bytes | EnhancedSmlFrame | str):
        if isinstance(_bytes, EnhancedSmlFrame):
            self.returns.append(_bytes)
        elif isinstance(_bytes, str):
            assert _bytes in 'CRC_ERROR'
            self.returns.append(_bytes)
        elif isinstance(_bytes, bytes):
            self.returns.append(None)
            super().add(_bytes)
        elif _bytes is None:
            pass
        else:
            raise TypeError()

    def clear(self):
        super().clear()

    def get_frame(self) -> EnhancedSmlFrame | None:
        if not self.returns:
            return super().get_frame()

        cmd = self.returns.pop(0)
        if cmd is None:
            return super().get_frame()

        if isinstance(cmd, EnhancedSmlFrame):
            return cmd

        if cmd == 'CRC_ERROR':
            raise CrcError(b'my_msg', 123456, 654321)

        raise ValueError()
