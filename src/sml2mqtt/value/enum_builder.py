from typing import Any, Dict, List, Type, TypeVar, Union

import sml2mqtt
from sml2mqtt.config.device import FilterOptionEnum, TransformOptionEnum, TYPE_SML_VALUE_FILTER_CFG, \
    TYPE_SML_VALUE_TRANSFORM_CFG, TYPE_SML_VALUE_WORKAROUND_CFG, WorkaroundOptionEnum
from sml2mqtt.value.filter import ChangeFilter, DiffAbsFilter, DiffFilterBase, DiffPercFilter, FILTER_OBJ, RefreshEvery
from sml2mqtt.value.transformations import FactorTransformation, \
    OffsetTransformation, RoundTransformation, TRANSFORM_OBJ
from sml2mqtt.value.workarounds import NegativeOnEnergyMeterStatus, WORKAROUND_OBJ

TYPE_A = TypeVar('TYPE_A')


def _from_config(cfg: Union[TYPE_SML_VALUE_FILTER_CFG, TYPE_SML_VALUE_TRANSFORM_CFG],
                 class_map: Dict[Any, Type[TYPE_A]]) -> List[TYPE_A]:
    if cfg is None:
        return []

    ret = []
    for entry in cfg:
        for key, cls in class_map.items():
            params = entry.get(key)
            if params is not None:
                ret.append(cls(params))
                break
        else:
            raise ValueError(f'Unknown type: {entry}')
    return ret


def filter_from_config(cfg: TYPE_SML_VALUE_FILTER_CFG) -> List[FILTER_OBJ]:
    class_dict = {
        FilterOptionEnum.diff: DiffAbsFilter,
        FilterOptionEnum.perc: DiffPercFilter,
        FilterOptionEnum.every: RefreshEvery,
    }
    filters = _from_config(cfg, class_dict)

    # Default filters
    for f in filters:
        if isinstance(f, RefreshEvery):
            break
    else:
        filters.append(RefreshEvery(sml2mqtt.CONFIG.general.republish_after))

    for f in filters:
        if isinstance(f, DiffFilterBase):
            break
    else:
        filters.append(ChangeFilter())

    return filters


def transform_from_config(cfg: TYPE_SML_VALUE_TRANSFORM_CFG) -> List[TRANSFORM_OBJ]:
    class_dict = {
        TransformOptionEnum.factor: FactorTransformation,
        TransformOptionEnum.round: RoundTransformation,
        TransformOptionEnum.offset: OffsetTransformation,
    }
    return _from_config(cfg, class_dict)


def workaround_from_config(cfg: TYPE_SML_VALUE_WORKAROUND_CFG) -> List[WORKAROUND_OBJ]:
    class_dict = {
        WorkaroundOptionEnum.negative_on_energy_meter_status: NegativeOnEnergyMeterStatus,
    }
    return _from_config(cfg, class_dict)
