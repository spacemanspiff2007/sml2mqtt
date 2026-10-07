from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sml2mqtt.errors import UnprocessedObisValuesReceivedError


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Final

    from typing_extensions import Self

    from sml2mqtt.const import SmlFrameValues
    from sml2mqtt.sml_value.sml_value import SmlValue


class SmlValues:
    __slots__ = ('_all_ids', '_log', '_log_on_receive', '_logged_missing', '_processed_ids', '_skipped_ids', '_values')

    def __init__(self, log: logging.Logger) -> None:
        self._log: Final = log
        self._logged_missing: frozenset[str] = frozenset()  # keep track of logged missing ids to log only once
        self._log_on_receive: frozenset[str] = frozenset()  # If we receive sporadic IDs we log reception only once
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

    def set_skipped(self, *obis_ids: str) -> Self:
        self._skipped_ids = frozenset(obis_ids)
        self._all_ids = self._processed_ids | self._skipped_ids
        return self

    def add_value(self, value: SmlValue) -> Self:
        self._processed_ids = self._processed_ids.union((value.obis, ))
        self._all_ids = self._processed_ids | self._skipped_ids
        self._values = (*self._values, value)
        return self

    def process_frame(self, frame: SmlFrameValues) -> None:
        for value in self._values:
            value.process_frame(frame)

        obis_in_frame: Final = frame.obis_ids()

        if self._log_on_receive:
            for _obis in self._log_on_receive:
                if _obis in frame.values:
                    self._log.info(f'OBIS id that was missing was received: {_obis}')
                    self._log_on_receive -= {_obis}

        if obis_in_frame == self._all_ids:
            return None

        # Not all obis processed
        if obis_not_processed := obis_in_frame - self._all_ids:
            entries_left = [frame.get_value(_obis) for _obis in sorted(obis_not_processed)]
            raise UnprocessedObisValuesReceivedError(*entries_left)

        # Processed obis not in frame, log every missing id only once
        if (obis_missing := self._processed_ids - obis_in_frame) and not obis_missing.issubset(self._logged_missing):
            self._log.warning(
                f'Configured OBIS id{"" if len(obis_missing) == 1 else "s"} '
                f'missing in frame: {", ".join(sorted(obis_missing))}!'
            )
            to_add = obis_missing - self._logged_missing

            self._logged_missing |= obis_missing
            self._log_on_receive |= to_add

        return None

    def describe(self) -> Generator[str, None, None]:
        yield f'Skipped: {", ".join(sorted(self._skipped_ids))}'
        yield ''
        for value in self._values:
            yield from value.describe()
