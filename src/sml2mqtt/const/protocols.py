from typing_extensions import Protocol


class DeviceProto(Protocol):
    @property
    def name(self) -> str:
        ...

    def on_source_data(self, data: bytes):
        ...

    def on_source_error(self, e: Exception):
        ...


class SourceProto(Protocol):
    async def start(self):
        ...

    async def stop(self):
        ...
