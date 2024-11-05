from __future__ import annotations

from smllib import SmlFrame, SmlStreamReader
from smllib.errors import CrcError

from sml2mqtt import CONFIG


class StreamReaderGroup:
    def __init__(self, *crcs: str) -> None:
        self.readers = [SmlStreamReader(crc=crc) for crc in crcs]
        self.last_reader: SmlStreamReader | None = None

    def add(self, _bytes: bytes) -> None:
        for reader in self.readers:
            reader.add(_bytes)

    def get_frame(self) -> SmlFrame | None:
        crc_errors = []
        last_frame: SmlFrame | None = None
        for reader in self.readers:
            try:
                if (ret := reader.get_frame()) is None:
                    continue

                if last_frame is not None:
                    msg = 'Multiple frames'
                    raise ValueError(msg)

                if self.last_reader is not None and self.last_reader is not reader:
                    msg = 'Reader changed'
                    raise ValueError(msg)

                self.last_reader = reader
                last_frame = ret
            except CrcError as e:
                crc_errors.append(e)

        if last_frame is not None:
            return last_frame

        # all readers issued a crc error -> propagate
        if len(crc_errors) == len(self.readers):
            raise crc_errors[0] from None

        return None

    def get_reader(self) -> SmlStreamReader:
        if self.last_reader is None:
            msg = 'Last reader not set'
            raise ValueError(msg)
        return self.last_reader


def create_stream_reader_group() -> StreamReaderGroup:
    crc_algorithms = CONFIG.general.crc
    return StreamReaderGroup(*crc_algorithms)
