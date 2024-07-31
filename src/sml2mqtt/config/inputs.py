from typing import Literal

import serial
from aiohttp import ClientTimeout
from easyconfig import BaseModel
from pydantic import (
    AnyHttpUrl,
    Field,
    StrictFloat,
    StrictInt,
    constr,
    field_validator,
    model_validator,
)
from typing_extensions import override

from sml2mqtt.config.types import log


class SmlSourceSettingsBase(BaseModel):
    def get_device_name(self) -> str:
        raise NotImplementedError()


class SerialSourceSettings(SmlSourceSettingsBase):
    type: Literal['serial']

    url: constr(strip_whitespace=True, min_length=1, strict=True) = Field(..., description='Device path')
    timeout: StrictInt | StrictFloat = Field(
        default=6, description='Seconds after which a timeout will be detected (default=6)')

    baudrate: int = Field(9600, in_file=False)
    parity: str = Field('None', in_file=False)
    stopbits: StrictInt | StrictFloat = Field(serial.STOPBITS_ONE, in_file=False, alias='stop bits')
    bytesize: int = Field(serial.EIGHTBITS, in_file=False, alias='byte size')

    @field_validator('baudrate')
    def _val_baudrate(cls, v):
        if v not in serial.Serial.BAUDRATES:
            msg = f'must be one of {list(serial.Serial.BAUDRATES)}'
            raise ValueError(msg)
        return v

    @field_validator('parity')
    def _val_parity(cls, v):
        # Short name
        if v in serial.PARITY_NAMES:
            return v

        # Name -> Short name
        parity_values = {_n: _v for _v, _n in serial.PARITY_NAMES.items()}
        if v not in parity_values:
            msg = f'must be one of {list(parity_values)}'
            raise ValueError(msg)
        return parity_values[v]

    @field_validator('stopbits')
    def _val_stopbits(cls, v):
        if v not in serial.Serial.STOPBITS:
            msg = f'must be one of {list(serial.Serial.STOPBITS)}'
            raise ValueError(msg)
        return v

    @field_validator('bytesize')
    def _val_bytesize(cls, v):
        if v not in serial.Serial.BYTESIZES:
            msg = f'must be one of {list(serial.Serial.BYTESIZES)}'
            raise ValueError(msg)
        return v

    @override
    def get_device_name(self) -> str:
        return self.url.split('/')[-1]


class HttpSourceSettings(SmlSourceSettingsBase):
    type: Literal['http']

    url: AnyHttpUrl = Field(..., description='Url')
    timeout: StrictInt | StrictFloat = Field(
        default=6, description='Seconds after which a timeout will be detected (default=6)')

    interval: StrictInt | StrictFloat = Field(default=2, description='Delay between requests', ge=0.1)
    user: str = Field(default='', description='User (if needed)')
    password: str = Field(default='', description='Password (if needed)')

    request_timeout: StrictInt | StrictFloat | None = Field(
        default=None, alias='request timeout', description='Dedicated timeout for the http request',
        in_file=False
    )

    @override
    def get_device_name(self) -> str:
        return self.url.host

    @model_validator(mode='after')
    def check_timeout_gt_interval(self):
        if self.interval * 2 > self.timeout:
            msg = 'Timeout must be greater equal than 2 * interval'
            raise ValueError(msg)

        # Timeout is interval, and we automatically retry 3 times before we fail
        if self.interval * 3 > self.timeout:
            log.warning(f'The recommendation for timeout is at least 3 * interval '
                        f'({self.interval * 3:.0f})! Currently: {self.timeout}')

        return self

    def get_request_timeout(self) -> ClientTimeout:
        value = self.interval if self.request_timeout is None else self.request_timeout
        if value is None:
            msg = 'No value for ClientTimeout'
            raise ValueError(msg)
        return ClientTimeout(total=value)
