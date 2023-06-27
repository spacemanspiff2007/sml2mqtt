from typing import Union

import serial
from easyconfig import BaseModel
from pydantic import AnyHttpUrl, confloat, constr, Field, StrictFloat, StrictInt, validator


class SmlSourceSettingsBase(BaseModel):
    def get_device_name(self) -> str:
        raise NotImplementedError()

    def get_device_id(self) -> str:
        raise NotImplementedError()


class PortSourceSettings(SmlSourceSettingsBase):
    url: constr(strip_whitespace=True, min_length=1, strict=True) = Field(..., description='Device path')
    timeout: Union[StrictInt, StrictFloat] = Field(
        default=3, description='Seconds after which a timeout will be detected (default=3)')

    baudrate: int = Field(9600, in_file=False)
    parity: str = Field('None', in_file=False)
    stopbits: Union[StrictInt, StrictFloat] = Field(serial.STOPBITS_ONE, in_file=False, alias='stop bits')
    bytesize: int = Field(serial.EIGHTBITS, in_file=False, alias='byte size')

    @validator('baudrate')
    def _val_baudrate(cls, v):
        if v not in serial.Serial.BAUDRATES:
            raise ValueError(f'must be one of {list(serial.Serial.BAUDRATES)}')
        return v

    @validator('parity')
    def _val_parity(cls, v):
        # Short name
        if v in serial.PARITY_NAMES:
            return v

        # Name -> Short name
        parity_values = {_n: _v for _v, _n in serial.PARITY_NAMES.items()}
        if v not in parity_values:
            raise ValueError(f'must be one of {list(parity_values)}')
        return parity_values[v]

    @validator('stopbits')
    def _val_stopbits(cls, v):
        if v not in serial.Serial.STOPBITS:
            raise ValueError(f'must be one of {list(serial.Serial.STOPBITS)}')
        return v

    @validator('bytesize')
    def _val_bytesize(cls, v):
        if v not in serial.Serial.BYTESIZES:
            raise ValueError(f'must be one of {list(serial.Serial.BYTESIZES)}')
        return v

    def get_device_name(self) -> str:
        return self.url.split("/")[-1]

    def get_device_id(self) -> str:
        return self.url.split("/")[-1]


class HttpSourceSettings(SmlSourceSettingsBase):
    url: AnyHttpUrl = Field(..., description='Url')
    timeout: Union[StrictInt, StrictFloat] = Field(
        default=3, description='Seconds after which a timeout will be detected (default=3)')

    interval: confloat(ge=0.1) = Field(default=1, description='Delay between requests')

    user: str = Field(default='', description='User (if needed)')
    password: str = Field(default='', description='Password (if needed)')

    def get_device_name(self) -> str:
        return self.url.host

    def get_device_id(self) -> str:
        return self.url.host
