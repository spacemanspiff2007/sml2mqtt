from __future__ import annotations

import traceback
from logging import DEBUG as LVL_DEBUG
from logging import INFO as LVL_INFO
from typing import TYPE_CHECKING, Any, Final

import smllib
from smllib import SmlStreamReader
from smllib.errors import CrcError
from typing_extensions import Self

from sml2mqtt import CONFIG
from sml2mqtt.__log__ import get_logger
from sml2mqtt.const import EnhancedSmlFrame
from sml2mqtt.errors import ObisIdForConfigurationMappingNotFoundError, Sml2MqttExceptionWithLog
from sml2mqtt.mqtt import BASE_TOPIC
from sml2mqtt.sml_device.sml_devices import ALL_DEVICES
from sml2mqtt.sml_value import SmlValues

from .device_status import DeviceStatus
from .setup_device import setup_device
from .stream_reader_group import StreamReaderGroup, create_stream_reader_group
from .watchdog import Watchdog


if TYPE_CHECKING:
    from collections.abc import Callable

    from sml2mqtt.const import SourceProto

# -------------------------------------------------------------------------------------------------
# Dirty:
# Replace the class SmlFrame which is returned by SmlStreamReader with EnhancedSmlFrame
assert hasattr(smllib.reader, 'SmlFrame')
setattr(smllib.reader, 'SmlFrame', EnhancedSmlFrame)


class SmlDevice:
    def __init__(self, name: str) -> None:
        self._name: Final = name
        self._source: SourceProto | None = None
        self.status: DeviceStatus = DeviceStatus.STARTUP

        self.watchdog: Final = Watchdog(self)
        self.stream_reader: StreamReaderGroup | SmlStreamReader = create_stream_reader_group()

        self.log = get_logger(self.name)
        self.log_status = self.log.getChild('status')

        self.mqtt_device: Final = BASE_TOPIC.create_child(self.name)
        self.mqtt_status: Final = self.mqtt_device.create_child('status')

        self.device_id: str | None = None
        self.sml_values: Final = SmlValues()

        self.frame_handler: Callable[[EnhancedSmlFrame], Any] = self.process_first_frame

    @property
    def name(self) -> str:
        return self._name

    def set_source(self, source: SourceProto) -> Self:
        assert self._source is None, self._source
        self._source = source
        return self

    async def start(self) -> None:
        if self._source is not None:
            self._source.start()
        self.watchdog.start()

    async def cancel_and_wait(self) -> None:
        if self._source is not None:
            await self._source.cancel_and_wait()
        await self.watchdog.cancel_and_wait()

    def set_status(self, new_status: DeviceStatus) -> bool:
        if (old_status := self.status) == new_status or old_status.is_shutdown_status():
            return False

        self.status = new_status

        # Don't log toggling between CRC_ERROR and OK. Only log if new status is not OK
        level = LVL_INFO
        if new_status is DeviceStatus.CRC_ERROR:
            level = LVL_DEBUG
        elif old_status is DeviceStatus.CRC_ERROR:
            if new_status is DeviceStatus.OK:
                level = LVL_DEBUG
            else:
                # Log old status if new status is not OK
                self.log_status.log(level, f'Old status {old_status:s}')

        self.log_status.log(level, f'{new_status:s}')
        self.mqtt_status.publish(new_status.value)

        ALL_DEVICES.check_status()
        return True

    def on_source_data(self, data: bytes) -> None:
        frame = None    # type: EnhancedSmlFrame | None

        try:
            self.watchdog.feed()
            self.stream_reader.add(data)

            try:
                if (frame := self.stream_reader.get_frame()) is None:
                    return None
            except CrcError as e:
                self.log.debug(f'Crc error: {e.crc_calc} != {e.crc_msg}')
                self.set_status(DeviceStatus.CRC_ERROR)
                return None

            # Process Frame
            self.frame_handler(frame)
        except Exception as e:
            # dump frame if possible
            if frame is not None:
                for line in frame.get_frame_str():
                    self.log.info(line)

            self.on_error(e)

    def on_error(self, e: Exception, *, show_traceback: bool = True) -> None:
        self.log.debug(f'Exception {type(e)}: "{e}"')

        # Log exception
        if isinstance(e, Sml2MqttExceptionWithLog):
            e.log_msg(self.log)
        else:
            if show_traceback:
                for line in traceback.format_exc().splitlines():
                    self.log.error(line)
            else:
                self.log.error(f'{type(e)}: {e}')

        # Signal that an error occurred
        self.set_status(DeviceStatus.ERROR)
        return None

    def on_source_failed(self, reason: str) -> None:
        self.log.error(f'Source failed: {reason}')
        self.set_status(DeviceStatus.SOURCE_FAILED)

    def on_timeout(self) -> None:
        self.set_status(DeviceStatus.MSG_TIMEOUT)

    def process_frame(self, frame: EnhancedSmlFrame) -> None:

        frame_values = frame.get_frame_values(self.log)

        self.sml_values.process_frame(frame_values)

        # There was no Error -> OK
        self.set_status(DeviceStatus.OK)

    def setup_values_from_frame(self, frame: EnhancedSmlFrame) -> None:
        if not isinstance(self.stream_reader, SmlStreamReader):
            self.stream_reader = self.stream_reader.get_reader()
            _func_name = self.stream_reader.crc_func.__name__
            crc_func_name = getattr(self.stream_reader.crc_func, '__module__', _func_name).rsplit('.', 1)[-1]
            self.log.debug(f'Using crc {crc_func_name:s}')

        frame_values = frame.get_frame_values(self.log)

        # search frame and see if we get a match
        for search_obis in CONFIG.general.device_id_obis:
            if (obis_value := frame_values.get_value(search_obis)) is not None:
                self.log.debug(f'Found obis id {search_obis:s} in the sml frame')
                self.device_id = str(obis_value.get_value())
                break
        else:
            searched = ', '.join(CONFIG.general.device_id_obis)
            self.log.error(f'Found none of the following obis ids in the sml frame: {searched:s}')
            raise ObisIdForConfigurationMappingNotFoundError()

        # Search configuration to see if we have a special config for the device
        device_cfg = CONFIG.devices.get(self.device_id)
        if device_cfg is None:
            self.log.warning(f'No device found for {self.device_id:s}')
        else:
            self.log.debug(f'Device found for {self.device_id:s}')
        setup_device(self, frame_values, device_cfg, CONFIG.general)

        self.frame_handler = self.process_frame

    def process_first_frame(self, frame: EnhancedSmlFrame) -> None:

        try:
            self.setup_values_from_frame(frame)
        except Exception as e:
            self.set_status(DeviceStatus.SHUTDOWN)
            self.on_error(e)
            return None

        self.frame_handler(frame)
        return None

    def analyze_frame(self, frame: EnhancedSmlFrame) -> None:

        # log Frame and frame description
        for line in frame.get_analyze_str():
            self.log.info(line)

        # Setup and process the frame
        self.setup_values_from_frame(frame)

        # Log setup values
        for line in self.sml_values.describe():
            self.log.info(line)

        # process the frame
        self.frame_handler(frame)

        # shutdown
        self.log.info('')
        self.set_status(DeviceStatus.SHUTDOWN)
        return None
