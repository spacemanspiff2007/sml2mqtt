from __future__ import annotations

from typing_extensions import Protocol


class DeviceProto(Protocol):
    @property
    def name(self) -> str:
        ...

    def on_source_data(self, data: bytes):
        ...

    def on_source_failed(self, reason: str):
        ...

    def on_error(self, e: Exception, *, show_traceback: bool = True):
        ...


class SourceProto(Protocol):
    def start(self):
        ...

    def cancel_and_wait(self):
        ...
