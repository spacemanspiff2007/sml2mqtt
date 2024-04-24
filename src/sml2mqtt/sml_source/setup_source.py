
from sml2mqtt.config.inputs import HttpSourceSettings, SerialSourceSettings
from sml2mqtt.const import DeviceProto, SourceProto


async def create_source(device: DeviceProto, settings: SerialSourceSettings | HttpSourceSettings) -> SourceProto:

    if isinstance(settings, SerialSourceSettings):
        from .serial import SerialSource
        return await SerialSource.create(device, settings)
    if isinstance(settings, HttpSourceSettings):
        from .http import HttpSource
        return await HttpSource.create(device, settings)

    msg = 'Unknown source input type'
    raise TypeError(msg)
