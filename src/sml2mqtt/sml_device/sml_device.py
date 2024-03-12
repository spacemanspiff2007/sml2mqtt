from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, Final

import smllib
from smllib import SmlStreamReader
from smllib.errors import CrcError

from sml2mqtt.__log__ import get_logger
from sml2mqtt.const import EnhancedSmlFrame
from sml2mqtt.device_old import DeviceStatus
from sml2mqtt.errors import Sml2MqttExceptionWithLog
from sml2mqtt.mqtt import BASE_TOPIC
from sml2mqtt.sml_value import SmlValues

from .watchdog import Watchdog


if TYPE_CHECKING:
    from collections.abc import Callable
    from sml2mqtt.const import SourceProto

# -------------------------------------------------------------------------------------------------
# Dirty:
# Replace the class SmlFrame which is returned by SmlStreamReader with EnhancedSmlFrame
assert hasattr(smllib.reader, 'SmlFrame')
setattr(smllib.reader, '', EnhancedSmlFrame)


class SmlDevice:
    def __init__(self, name: str):
        self._name: Final = name
        self._source: SourceProto | None = None
        self.status: DeviceStatus = DeviceStatus.STARTUP

        self.watchdog: Final = Watchdog(self)
        self.stream_reader: Final = SmlStreamReader()

        self.log = get_logger(self.name)
        self.log_status = self.log.getChild('status')

        self.mqtt_device: Final = BASE_TOPIC.create_child(self.name)
        self.mqtt_status: Final = self.mqtt_device.create_child('status')

        self.sml_values: Final = SmlValues()

        self.frame_handler: Callable[[EnhancedSmlFrame], Any] = self.process_frame

    @property
    def name(self) -> str:
        return self._name

    def set_source(self, source: SourceProto):
        assert self._source is None, self._source
        self._source = source
        return self

    async def start(self):
        if self._source is not None:
            await self._source.start()
        await self.watchdog.start()

    async def stop(self):
        if self._source is not None:
            await self._source.stop()
        await self.watchdog.stop()

    def set_status(self, new_status: DeviceStatus) -> bool:
        if self.status == new_status:
            return False

        self.status = new_status
        self.log_status.info(f'{new_status:s}')
        self.mqtt_status.publish(new_status.value)
        return True

    def on_source_data(self, data: bytes):
        frame = None    # type: EnhancedSmlFrame | None

        try:
            self.watchdog.feed()
            self.stream_reader.add(data)

            try:
                if (frame := self.stream_reader.get_frame()) is None:
                    return None
            except CrcError as e:
                self.log.error(f'Crc error: {e.crc_calc} != {e.crc_msg}')
                self.set_status(DeviceStatus.CRC_ERROR)
                return None

            # Process Frame
            self.frame_handler(frame)
        except Exception as e:
            # dump frame if possible
            if frame is not None:
                frame.log_frame(self.log)

            # Log exception
            if isinstance(e, Sml2MqttExceptionWithLog):
                e.log_msg(self.log)
            else:
                for line in traceback.format_exc().splitlines():
                    self.log.error(line)

            # Signal that an error occurred
            self.set_status(DeviceStatus.ERROR)
            return None

    def on_source_error(self, e: Exception):
        pass

    def on_timeout(self):
        pass

    def process_frame(self, frame: EnhancedSmlFrame):

        frame_values = frame.get_frame_values(self.log)

        self.sml_values.process_frame(frame_values)

        # There was no Error -> OK
        self.set_status(DeviceStatus.OK)
