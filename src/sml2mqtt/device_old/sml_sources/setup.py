from typing import TYPE_CHECKING, Union

import sml2mqtt
from sml2mqtt.config.config import SerialSourceSettings
from sml2mqtt.config.source import HttpSourceSettings

if TYPE_CHECKING:
    from .sml_http import HttpSource
    from .sml_serial import SerialSource


async def create_source(
        settings: Union[SerialSourceSettings, HttpSourceSettings],
        device: 'sml2mqtt.device.Device') -> Union['SerialSource', 'HttpSource']:

    if isinstance(settings, SerialSourceSettings):
        from .sml_serial import SerialSource
        return await SerialSource.create(settings, device)
    if isinstance(settings, HttpSourceSettings):
        from .sml_http import HttpSource
        return await HttpSource.create(settings, device)

    raise ValueError('Unknown config type')
