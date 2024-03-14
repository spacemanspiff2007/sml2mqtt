import sml2mqtt.device_old
from sml2mqtt.config.config import SerialSourceSettings


class SmlSourceBase:

    @classmethod
    async def create(cls, settings: SerialSourceSettings, device: 'sml2mqtt.device.Device'):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()

    async def wait_for_stop(self):
        raise NotImplementedError()
