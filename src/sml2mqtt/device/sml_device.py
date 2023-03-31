import logging
import traceback
from asyncio import Event
from binascii import b2a_hex
from typing import Dict, Final, List, Optional, Set

from smllib import SmlFrame, SmlStreamReader
from smllib.errors import CrcError
from smllib.sml import SmlListEntry

import sml2mqtt
from sml2mqtt import CMD_ARGS
from sml2mqtt.__log__ import get_logger
from sml2mqtt.__shutdown__ import shutdown
from sml2mqtt.config import CONFIG
from sml2mqtt.config.config import PortSettings
from sml2mqtt.config.device import SmlDeviceConfig, SmlValueConfig
from sml2mqtt.device import DeviceStatus
from sml2mqtt.device.watchdog import Watchdog
from sml2mqtt.errors import AllDevicesFailedError, DeviceSetupFailedError, \
    ObisIdForConfigurationMappingNotFoundError, Sml2MqttConfigMappingError
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.sml_value import SmlValue

Event().set()

ALL_DEVICES: Dict[str, 'Device'] = {}


class Device:
    @classmethod
    async def create(cls, settings: PortSettings, timeout: float, skip_values: Set[str], mqtt_device: MqttObj):
        device = None
        try:
            device = cls(settings.url, timeout, set(skip_values), mqtt_device)
            device.serial = await sml2mqtt.device.SmlSerial.create(settings, device)
            ALL_DEVICES[settings.url] = device

            return device
        except Exception as e:
            if device is None:
                get_logger('device').error('Setup failed!')
            else:
                device.log.error('Setup failed')
            raise DeviceSetupFailedError(e) from None

    def __init__(self, url: str, timeout: float, skip_values: Set[str], mqtt_device: MqttObj):
        self.stream = SmlStreamReader()
        self.serial: 'sml2mqtt.device.SmlSerial' = None
        self.watchdog: Final = Watchdog(timeout, self.serial_data_timeout)

        self.status: DeviceStatus = DeviceStatus.STARTUP
        self.mqtt_device: MqttObj = mqtt_device
        self.mqtt_status: MqttObj = mqtt_device.create_child('status')

        self.log = get_logger(url.split("/")[-1])
        self.log_status = get_logger(url.split("/")[-1]).getChild('status')

        self.device_url = url
        self.device_id: str = url.split("/")[-1]

        self.sml_values: Dict[str, SmlValue] = {}

        self.skip_values = skip_values

    def start(self):
        self.serial.start()
        self.watchdog.start()

    def stop(self):
        self.serial.cancel()
        self.watchdog.cancel()

    def __await__(self):
        yield from self.serial.wait_for_cancel().__await__()
        yield from self.watchdog.wait_for_cancel().__await__()

    def shutdown(self):
        if not self.status.is_shutdown_status():
            self.set_status(DeviceStatus.SHUTDOWN)

    def set_status(self, new_status: DeviceStatus) -> bool:
        if self.status == new_status:
            return False

        self.status = new_status
        self.log_status.info(f'{new_status:s}')

        # Don't publish the port open because we don't have the correct name from the config yet
        if new_status != DeviceStatus.PORT_OPENED:
            self.mqtt_status.publish(new_status.value)

        # If all ports are closed, or we have errors we shut down
        if all(x.status.is_shutdown_status() for x in ALL_DEVICES.values()):
            # Stop reading from the serial port because we are shutting down
            self.serial.close()
            self.watchdog.cancel()
            shutdown(AllDevicesFailedError)
        return True

    def _select_device_id(self, frame_values: Dict[str, SmlListEntry]) -> str:
        # search frame and see if we get a match
        for search_obis in CONFIG.general.device_id_obis:
            if (obis_value := frame_values.get(search_obis)) is not None:
                self.log.debug(f'Found obis id {search_obis:s} in the sml frame')
                value = obis_value.get_value()
                self.device_id = str(value)
                return str(search_obis)

        searched = ', '.join(CONFIG.general.device_id_obis)
        self.log.error(f'Found none of the following obis ids in the sml frame: {searched:s}')
        raise ObisIdForConfigurationMappingNotFoundError()

    def _select_device_config(self) -> Optional[SmlDeviceConfig]:
        device_cfg = CONFIG.devices.get(self.device_id)
        if device_cfg is None:
            self.log.warning(f'No configuration found for {self.device_id:s}')
            return None

        self.log.debug(f'Configuration found for {self.device_id:s}')
        return device_cfg

    def _setup_device(self, frame_values: Dict[str, SmlListEntry]):
        found_obis = self._select_device_id(frame_values)
        cfg = self._select_device_config()

        # Global configuration option to ignore mapping value
        if not CONFIG.general.report_device_id:
            self.skip_values.add(found_obis)

        # Change the mqtt topic default from device url to the matched device id
        self.mqtt_device.set_topic(self.device_id)

        # override from config
        if cfg is not None:
            # setup topics
            self.mqtt_device.set_config(cfg.mqtt)
            self.mqtt_status.set_config(cfg.status)

            # additional obis values that are ignored from the config
            if cfg.skip is not None:
                self.skip_values.update(cfg.skip)

        self._setup_sml_values(cfg, frame_values)

    def _setup_sml_values(self, device_config: Optional[SmlDeviceConfig], frame_values: Dict[str, SmlListEntry]):
        log_level = logging.DEBUG if not CMD_ARGS.analyze else logging.INFO
        values_config: Dict[str, SmlValueConfig] = device_config.values if device_config is not None else {}

        from_frame = frozenset(frame_values) - self.skip_values
        from_config = frozenset(values_config)
        default_cfg = from_frame - from_config

        # create entries where we don't have a user config
        for obis_id in sorted(default_cfg):
            self.log.log(log_level, f'Creating default value handler for {obis_id}')
            self.sml_values[obis_id] = SmlValue(
                self.device_id, obis_id, self.mqtt_device.create_child(obis_id),
                workarounds=[], transformations=[], filters=sml2mqtt.sml_value.filter_from_config(None)
            )

        # create entries which are defined by the user
        for obis_id, value_config in sorted(values_config.items()):
            # little helper to catch config errors
            if obis_id in self.skip_values:
                self.log.warning(f'Config for {obis_id:s} found but {obis_id:s} is also marked to be skipped')
            if obis_id not in frame_values:
                self.log.warning(f'Config for {obis_id:s} found but {obis_id:s} was not reported by the frame')

            self.log.log(log_level, f'Creating value handler from config for {obis_id}')
            self.sml_values[obis_id] = SmlValue(
                self.device_id, obis_id, self.mqtt_device.create_child(obis_id).set_config(value_config.mqtt),
                workarounds=sml2mqtt.sml_value.workaround_from_config(value_config.workarounds),
                transformations=sml2mqtt.sml_value.transform_from_config(value_config.transformations),
                filters=sml2mqtt.sml_value.filter_from_config(value_config.filters),
            )

    def serial_data_timeout(self):
        if self.set_status(DeviceStatus.MSG_TIMEOUT):
            self.stream.clear()
            self.log.warning('Timeout')

    def serial_data_read(self, data: bytes):
        frame = None

        try:
            self.watchdog.feed()
            self.stream.add(data)

            try:
                frame = self.stream.get_frame()
                if frame is None:
                    return None
            except CrcError as e:
                self.log.error(f'Crc error: {e.crc_calc} != {e.crc_msg}')
                self.set_status(DeviceStatus.CRC_ERROR)
                return None

            # Process Frame
            self.process_frame(frame)
        except Exception as e:
            # dump frame if possible
            if frame is not None:
                self.log.error('Received Frame')
                self.log.error(f' -> {b2a_hex(frame.buffer)}')

            # Log exception
            if isinstance(e, Sml2MqttConfigMappingError):
                self.log.error(str(e))
            else:
                for line in traceback.format_exc().splitlines():
                    self.log.error(line)

            # Signal that an error occurred
            self.set_status(DeviceStatus.ERROR)
            return None

    def process_frame(self, frame: SmlFrame):

        do_analyze = sml2mqtt.CMD_ARGS.analyze
        do_wh_in_kwh = CONFIG.general.wh_in_kwh
        report_blank_meters = CONFIG.general.report_blank_energy_meters

        if do_analyze:
            self.log.info('')
            self.log.info('Received Frame')
            self.log.info(f' -> {b2a_hex(frame.buffer)}')
            self.log.info('')
            for obj in frame.parse_frame():
                for line in obj.format_msg().splitlines():
                    self.log.info(line)
            self.log.info('')

        # try shortcut, if that fails try parsing the whole frame
        try:
            sml_objs: List[SmlListEntry] = frame.get_obis()
        except Exception:
            self.log.info('get_obis failed - try parsing frame')
            for line in traceback.format_exc().splitlines():
                self.log.debug(line)

            sml_objs: List[SmlListEntry] = []
            for msg in frame.parse_frame():
                for val in getattr(msg.message_body, 'val_list', []):
                    sml_objs.append(val)

        frame_values: Dict[str, SmlListEntry] = {}
        for sml_obj in sml_objs:
            name = sml_obj.obis
            if name in self.skip_values:
                continue

            # Unit is Wh -> Value is from an Energy Meter
            if sml_obj.unit == 30:
                # We Don't publish disabled energy meters (always 0)
                if sml_obj.get_value() < 0.1 and not report_blank_meters:
                    continue
                # Global option to automatically convert from Wh to kWh
                if do_wh_in_kwh:
                    sml_obj.value /= 1000

            # Mark for publishing
            frame_values[name] = sml_obj

        # If we don't have the values we have to set up the device first
        if not self.sml_values:
            self._setup_device(frame_values)
            for drop_obis in self.skip_values:
                frame_values.pop(drop_obis, None)

        for obis_id, frame_value in frame_values.items():
            if (sml_value := self.sml_values.get(obis_id)) is not None:
                sml_value.set_value(frame_value, frame_values)
            else:
                # This can only happen if the device does not report all values with the initial frame
                # The user then has to skip the obis ids or manually add them to the configuration
                self.log.error('Unexpected obis id received!')
                for line in frame_value.format_msg().splitlines():
                    self.log.error(line)
                self.set_status(DeviceStatus.ERROR)
                return None

        # There was no Error -> OK
        self.set_status(DeviceStatus.OK)

        if do_analyze:
            for value in self.sml_values.values():
                self.log.info('')
                for line in value.describe().splitlines():
                    self.log.info(line)

            self.log.info('')
            self.set_status(DeviceStatus.SHUTDOWN)
            return None
