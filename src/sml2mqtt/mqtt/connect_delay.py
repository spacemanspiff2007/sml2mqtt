from asyncio import sleep
from typing import Optional


class DynDelay:
    def __init__(self, min_delay: float, max_delay: float, start_delay: Optional[float] = None):
        if min_delay < 0:
            raise ValueError(f'min_delay must be >= 0: {min_delay}')
        if max_delay <= min_delay:
            raise ValueError(f'max_delay must be >= min_delay: {max_delay}')

        self.min = min_delay
        self.max = max_delay

        if start_delay is None:
            start_delay = min_delay

        self.curr = max(min(start_delay, max_delay), min_delay)

    async def wait(self):
        await sleep(self.curr)

    def increase(self):
        self.curr = min(self.max, self.curr * 2)
        if not self.curr:
            self.curr = 1

    def reset(self):
        self.curr = self.min

    async def __aenter__(self):
        await self.wait()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.reset()
        else:
            self.increase()
        return False
