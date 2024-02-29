import sml2mqtt.device
from sml2mqtt.config.config import PortSourceSettings


class SmlSourceBase:

    @classmethod
    async def create(cls, settings: PortSourceSettings, device: 'sml2mqtt.device.Device'):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()

    async def wait_for_stop(self):
        raise NotImplementedError()
