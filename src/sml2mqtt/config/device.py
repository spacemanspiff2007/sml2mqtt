from enum import Enum
from typing import Dict, List, Optional, Set, Union

from easyconfig import BaseModel
from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr, validator

from .mqtt import OptionalMqttPublishConfig

REPUBLISH_ALIAS = 'republish after'


class WorkaroundOptionEnum(str, Enum):
    negative_on_energy_meter_status = 'negative on energy meter status'


class TransformOptionEnum(str, Enum):
    factor = 'factor'
    offset = 'offset'
    round = 'round'


class FilterOptionEnum(str, Enum):
    diff = 'diff'
    perc = 'perc'
    every = 'every'


TYPE_SML_VALUE_WORKAROUND_CFG = \
    Optional[List[Dict[WorkaroundOptionEnum, Union[StrictBool, StrictInt, StrictFloat, StrictStr]]]]
TYPE_SML_VALUE_TRANSFORM_CFG = Optional[List[Dict[TransformOptionEnum, Union[StrictInt, StrictFloat]]]]
TYPE_SML_VALUE_FILTER_CFG = Optional[List[Dict[FilterOptionEnum, Union[StrictInt, StrictFloat]]]]


class SmlValueConfig(BaseModel):
    mqtt: OptionalMqttPublishConfig = Field(None, description='Mqtt config for this entry (optional)')

    workarounds: TYPE_SML_VALUE_WORKAROUND_CFG = Field(
        None, description='Workarounds for the value (optional)')
    transformations: TYPE_SML_VALUE_TRANSFORM_CFG = Field(
        None, description='Mathematical transformations for the value (optional)')
    filters: TYPE_SML_VALUE_FILTER_CFG = Field(
        None, description='Refresh options for the value (optional)')

    @validator('workarounds', 'transformations', 'filters')
    def len_1(cls, v):
        if v is None:
            return None

        for entry in v:
            if len(entry) != 1:
                raise ValueError(f'Only one entry allowed! Got {len(entry)}: {", ".join(entry.keys())}')
        return v


class SmlDeviceConfig(BaseModel):
    mqtt: Optional[OptionalMqttPublishConfig] = OptionalMqttPublishConfig()
    status: Optional[OptionalMqttPublishConfig] = OptionalMqttPublishConfig(topic='status')

    skip: Optional[Set[StrictStr]] = Field(
        default=None, description='OBIS codes (HEX) of values that will not be published (optional)')

    values: Optional[Dict[str, SmlValueConfig]] = Field(
        default=None, description='Special configurations for each of the values (optional)')
