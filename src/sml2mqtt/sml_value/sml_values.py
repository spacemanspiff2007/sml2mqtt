from __future__ import annotations

from typing import TYPE_CHECKING

from sml2mqtt.errors import RequiredObisValueNotInFrameError, UnprocessedObisValuesReceivedError


if TYPE_CHECKING:
    from collections.abc import Generator

    from sml2mqtt.const import SmlFrameValues
    from sml2mqtt.sml_value.sml_value import SmlValue


class SmlValues:
    def __init__(self) -> None:
        self._processed_ids: frozenset[str] = frozenset()
        self._skipped_ids: frozenset[str] = frozenset()
        self._all_ids: frozenset[str] = frozenset()
        self._values: tuple[SmlValue, ...] = ()

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__:s} '
            f'processed={",".join(self._processed_ids):s}, '
            f'skipped={",".join(self._skipped_ids):s}>'
        )

    def set_skipped(self, *obis_ids: str):
        self._skipped_ids = frozenset(obis_ids)
        self._all_ids = self._processed_ids | self._skipped_ids
        return self

    def add_value(self, value: SmlValue):
        self._processed_ids = self._processed_ids.union((value.obis, ))
        self._all_ids = self._processed_ids | self._skipped_ids
        self._values = (*self._values, value)
        return self

    def process_frame(self, frame: SmlFrameValues):
        for value in self._values:
            value.process_frame(frame)

        obis_in_frame = frame.obis_ids()

        # Not all obis processed
        if obis_left := obis_in_frame - self._all_ids:
            entries_left = [frame.get_value(_obis) for _obis in sorted(obis_left)]
            raise UnprocessedObisValuesReceivedError(*entries_left)

        # Processed obis not in frame
        if obis_missing := self._processed_ids - obis_in_frame:
            raise RequiredObisValueNotInFrameError(*sorted(obis_missing))

    def describe(self) -> Generator[str, None, None]:
        yield f'Skipped: {", ".join(sorted(self._skipped_ids))}'
        yield ''
        for value in self._values:
            yield from value.describe()
