import logging
import traceback
from asyncio import create_task
from binascii import b2a_hex
from time import monotonic
from typing import Any, Dict, List, Optional, Set, Tuple

from smllib import CrcError, SmlStreamReader

import sml2mqtt._args
import sml2mqtt.sml_serial
from ._signals import stop_loop
from .config import CONFIG
from .mqtt import publish
from .sml_device_status import DeviceStatus
from .sml_serial import log as serial_log

ALL: Dict[str, 'Device'] = {}


class Device:
    @classmethod
    async def create(cls, url: str, timeout: float, skip_values: List[str]):
        c = cls(url, set(skip_values))
        c.serial = await sml2mqtt.sml_serial.SmlSerial.create(url, c, timeout)
        ALL[url] = c
        return c

    def __init__(self, url: str, skip_values: Set[str]):
        self.stream = SmlStreamReader()
        self.status: Optional[DeviceStatus] = None

        self.serial: 'sml2mqtt.sml_serial.SmlSerial' = None
        self.device_name = url.lower()

        self.log = logging.getLogger(f'sml.device.{url.split("/")[-1]}')

        self.skip_values = skip_values

        self.value_cache: Dict[str, Tuple[float, Any]] = {}

    def set_status(self, new_status: DeviceStatus):
        if self.status == new_status:
            return None
        self.status = new_status

        # DeviceStatus.PORT_OPENED -> PORT_OPENED
        _stat = str(new_status).split('.')[-1]
        self.log.info(f'{_stat}')

        # Don't publish the port open because we don't have the correct name yet
        if new_status != DeviceStatus.PORT_OPENED:
            create_task(
                publish(CONFIG.mqtt.topics.get_topic(self.device_name, 'status'), _stat)
            )

        # If all ports are closed or we have errors we shut down
        if all(map(lambda x: x.status in (DeviceStatus.PORT_CLOSED, DeviceStatus.ERROR, DeviceStatus.SHUTDOWN),
                   ALL.values())):
            create_task(stop_loop())

    def publish_value(self, name: str, value):
        create_task(
            publish(CONFIG.mqtt.topics.get_topic(self.device_name, name), value)
        )

    async def read(self):
        try:
            try:
                frame = self.stream.get_frame()
                if frame is None:
                    return None
            except CrcError as e:
                serial_log.error(f'Crc error on {self.serial.url}: {e.crc_calc} != {e.crc_msg}')
                self.set_status(DeviceStatus.CRC_ERROR)
                return None

            if sml2mqtt._args.ARGS.analyze:
                self.log.info('')
                self.log.info('Received Frame')
                self.log.info(f' -> {b2a_hex(frame.buffer)}')
                self.log.info('')
                for obj in frame.parse_frame():
                    for line in obj.format_msg().splitlines():
                        self.log.info(line)
                self.set_status(DeviceStatus.SHUTDOWN)
                return None

            vals = {}
            for sml_obj in frame.get_obis():
                name = sml_obj.obis
                if name in self.skip_values:
                    continue

                value = sml_obj.get_value()

                # We overwrite the device name with the unique identifier
                if name == '0100000009ff':
                    self.device_name = str(value)
                    continue

                # Wh -> kWh
                if sml_obj.unit == 30:
                    # Don't publish disabled energy meters
                    if value < 0.1:
                        continue
                    value = round(value / 1000, 2)

                # Check value cache
                now = monotonic()
                try:
                    c_time, c_value = self.value_cache[name]
                    if value == c_value and now - c_time < CONFIG.general.max_wait:
                        continue
                except KeyError:
                    pass
                self.value_cache[name] = now, value

                # Mark for publishing
                vals[name] = value

            # publish parsed objs
            for n, v in vals.items():
                self.publish_value(n, v)

            # Everything is okay when there are no errors
            if self.status != DeviceStatus.OK:
                self.set_status(DeviceStatus.OK)

        except Exception:
            for line in traceback.format_exc().splitlines():
                self.log.error(line)

            # Signal that an error occured
            self.set_status(DeviceStatus.ERROR)

            # Stop reading from the serial port
            self.serial.close()

        return None
