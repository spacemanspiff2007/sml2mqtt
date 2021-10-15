from time import monotonic
from typing import Any, Final


class RefreshMarker:
    def __init__(self, refresh_time: float):
        if refresh_time <= 0:
            raise ValueError('Refresh time must be > 0')

        self._refresh_time: Final = refresh_time
        self._last_refresh: float = monotonic()

        self._last_value: Any = None

    def required(self, value: Any) -> bool:
        if value is not None and value != self._last_value:
            return True

        if monotonic() - self._last_refresh >= self._refresh_time:
            return True

        return False

    def done(self, value: Any):
        self._last_refresh = monotonic()
        self._last_value = value
