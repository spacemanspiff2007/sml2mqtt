from time import monotonic
from typing import Any, Final, Optional

from .base import FilterBase


class RefreshEvery(FilterBase):
    def __init__(self, refresh_time: float):
        if refresh_time <= 0:
            raise ValueError('Refresh time must be > 0')

        self._refresh_time: Final = refresh_time
        self._last_refresh: Optional[float] = None

        self._last_value: Any = None

    def required(self, value: Any) -> bool:
        if self._last_refresh is None:
            return True

        if monotonic() - self._last_refresh >= self._refresh_time:
            return True

        return False

    def done(self, value: Any):
        self._last_refresh = monotonic()
        self._last_value = value

    def __repr__(self):
        return f'<Every: {self._refresh_time}>'
