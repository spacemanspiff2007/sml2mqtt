import traceback
from binascii import b2a_hex
from typing import Dict, Final, Optional, Set

from smllib import SmlFrame, SmlStreamReader
from smllib.errors import CrcError
from smllib.sml import SmlListEntry

import sml2mqtt
from sml2mqtt import process_value
from sml2mqtt.__log__ import get_logger
from sml2mqtt.__shutdown__ import shutdown
from sml2mqtt.config import CONFIG
from sml2mqtt.config.device import SmlDeviceConfig
from sml2mqtt.device import DeviceStatus
from sml2mqtt.device.watchdog import Watchdog
from sml2mqtt.errors import AllDevicesFailed, DeviceSetupFailed
from sml2mqtt.mqtt import MqttObj
from sml2mqtt.process_value import VALUES as ALL_VALUES

ALL_DEVICES: Dict[str, 'Device'] = {}


class Device:
    @classmethod
    async def create(cls, url: str, timeout: float, skip_values: Set[str], mqtt_device: MqttObj):
        try:
            device = cls(url, timeout, set(skip_values), mqtt_device)
            device.serial = await sml2mqtt.device.SmlSerial.create(url, device)
            ALL_DEVICES[url] = device
            return device
        except Exception as e:
            raise DeviceSetupFailed(e) from None

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
        self.device_id_set = False

        self.skip_values = skip_values

    def shutdown(self):
        if not self.status.is_shutdown_status():
            self.set_status(DeviceStatus.SHUTDOWN)

    def set_status(self, new_status: DeviceStatus) -> bool:
        if self.status == new_status:
            return False

        self.status = new_status
        self.log_status.info(f'{new_status:s}')

        # Don't publish the port open because we don't have the correct name yet
        if new_status != DeviceStatus.PORT_OPENED:
            self.mqtt_status.publish(new_status.value)

        # If all ports are closed, or we have errors we shut down
        if all(map(lambda x: x.status.is_shutdown_status(), ALL_DEVICES.values())):
            # Stop reading from the serial port because we are shutting down
            self.serial.close()
            shutdown(AllDevicesFailed)
        return True

    def process_device_id(self, serial: str):
        assert isinstance(serial, str)
        self.device_id = serial
        self.device_id_set = True

        # config is optional
        cfg: Optional[SmlDeviceConfig] = None
        if CONFIG.devices is not None:
            cfg = CONFIG.devices.get(serial)

        # Build the defaults but with the serial number instead of the url
        if cfg is None:
            self.mqtt_device.set_topic(serial)
            return None

        # config found -> load all configured values
        self.mqtt_device.set_config(cfg.mqtt)
        self.mqtt_status.set_config(cfg.status)

        if cfg.skip is not None:
            self.skip_values.update(cfg.skip)

    def serial_data_timeout(self):
        if self.set_status(DeviceStatus.MSG_TIMEOUT):
            self.stream.clear()
            self.log.warning('Timeout')

    async def serial_data_read(self, data: bytes):
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
            await self.process_frame(frame)
        except Exception:
            # dump frame if possible
            if frame is not None:
                self.log.error('Received Frame')
                self.log.error(f' -> {b2a_hex(frame.buffer)}')

            # Log exception
            for line in traceback.format_exc().splitlines():
                self.log.error(line)

            # Signal that an error occurred
            self.set_status(DeviceStatus.ERROR)
            return None

    async def process_frame(self, frame: SmlFrame):

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

        frame_values: Dict[str, SmlListEntry] = {}
        for sml_obj in frame.get_obis():
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

        # We overwrite the device_id url (default) with the serial number if the device reports it
        # Otherwise we still do the config lookup so the user can configure the mqtt topics
        if not self.device_id_set:
            entry = frame_values.pop('0100000009ff', None)
            if entry is not None:
                if not CONFIG.general.report_device_id:
                    self.skip_values.add('0100000009ff')
                self.process_device_id(entry.get_value())
            else:
                self.process_device_id(self.device_url)

            # remove additionally skipped frames
            for name in self.skip_values:
                frame_values.pop(name, None)

        # Process all values
        for obis_value in frame_values.values():
            process_value(self, obis_value, frame_values)

        # There was no Error -> OK
        self.set_status(DeviceStatus.OK)

        if do_analyze:
            for obis, value in ALL_VALUES.get(self.device_id, {}).items():
                self.log.info('')
                for line in value.describe().splitlines():
                    self.log.info(line)

            self.log.info('')
            self.set_status(DeviceStatus.SHUTDOWN)
            return None
