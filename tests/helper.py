from asyncio import sleep
from collections.abc import Callable
from unittest.mock import Mock


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
