from asyncio import sleep
from types import TracebackType


class DynDelay:
    def __init__(self, min_delay: float, max_delay: float, start_delay: float | None = None) -> None:
        if min_delay < 0:
            msg = f'min_delay must be >= 0: {min_delay}'
            raise ValueError(msg)
        if max_delay <= min_delay:
            msg = f'max_delay must be >= min_delay: {max_delay}'
            raise ValueError(msg)

        self.min = min_delay
        self.max = max_delay

        if start_delay is None:
            start_delay = min_delay

        self.curr = max(min(start_delay, max_delay), min_delay)

    async def wait(self) -> None:
        await sleep(self.curr)

    def increase(self) -> None:
        self.curr = min(self.max, self.curr * 2)
        if not self.curr:
            self.curr = 1

    def reset(self) -> None:
        self.curr = self.min

    async def __aenter__(self) -> None:
        await self.wait()

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:  # noqa: E501
        if exc_type is None:
            self.reset()
        else:
            self.increase()
        return False
