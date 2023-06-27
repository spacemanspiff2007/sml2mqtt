from typing import Union

import sml2mqtt
from sml2mqtt.config.config import PortSourceSettings

from ...config.source import HttpSourceSettings
from .sml_http import HttpSource
from .sml_serial import SerialSource


async def create_source(
        settings: Union[PortSourceSettings, HttpSourceSettings],
        device: 'sml2mqtt.device.Device') -> Union[SerialSource, HttpSource]:

    if isinstance(settings, PortSourceSettings):
        return await SerialSource.create(settings, device)
    if isinstance(settings, HttpSourceSettings):
        return await HttpSource.create(settings, device)

    raise ValueError('Unknown config type')
