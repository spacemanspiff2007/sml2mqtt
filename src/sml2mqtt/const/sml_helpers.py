from __future__ import annotations

from binascii import b2a_hex
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

from smllib import SmlFrame


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from logging import Logger

    from smllib.sml import SmlListEntry


class EnhancedSmlFrame(SmlFrame):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.timestamp: Final = monotonic()

    def get_frame_str(self):
        yield 'Received Frame'
        yield f' -> {b2a_hex(self.buffer)}'

    def get_analyze_str(self) -> Generator[str, None, None]:
        yield ''
        yield from self.get_frame_str()
        yield ''
        for obj in self.parse_frame():
            yield from obj.format_msg().splitlines()
        yield ''

    def get_frame_values(self, log: Logger) -> SmlFrameValues:

        # try shortcut, if that fails try parsing the whole frame
        try:
            sml_objs = self.get_obis()  # type: list[SmlListEntry]
        except Exception:
            log.info('get_obis failed - try parsing frame')

            sml_objs = []   # type: list[SmlListEntry]
            for msg in self.parse_frame():
                for val in getattr(msg.message_body, 'val_list', []):
                    sml_objs.append(val)

        return SmlFrameValues.create(self.timestamp, sml_objs)


class SmlFrameValues:
    @classmethod
    def create(cls, timestamp: float, values: Iterable[SmlListEntry]):
        c = cls(timestamp)
        for value in values:
            c.values[value.obis] = value
        return c

    def __init__(self, timestamp: float) -> None:
        self.timestamp: Final = timestamp
        self.values: Final[dict[str, SmlListEntry]] = {}

    def __getattr__(self, item: str) -> SmlListEntry:
        return self.values[item]

    def __len__(self) -> int:
        return len(self.values)

    def get_value(self, obis: str) -> SmlListEntry | None:
        return self.values.get(obis)

    def obis_ids(self) -> frozenset[str]:
        return frozenset(self.values)

    def items(self, skip: set[str]) -> Generator[tuple[str, SmlListEntry], Any, None]:
        for obis_id, value in self.values.items():
            if obis_id in skip:
                continue
            yield obis_id, value
