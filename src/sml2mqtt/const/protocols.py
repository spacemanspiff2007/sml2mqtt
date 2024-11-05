from __future__ import annotations

from typing_extensions import Protocol


class DeviceProto(Protocol):
    @property
    def name(self) -> str:
        ...

    def on_source_data(self, data: bytes) -> None:
        ...

    def on_source_failed(self, reason: str) -> None:
        ...

    def on_error(self, e: Exception, *, show_traceback: bool = True) -> None:
        ...


class SourceProto(Protocol):
    def start(self) -> None:
        ...

    def cancel_and_wait(self) -> None:
        ...
