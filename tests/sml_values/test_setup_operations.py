import inspect
import types
from datetime import time
from typing import Annotated, Union, get_args, get_origin

import pytest

from sml2mqtt.config.operations import Sequence, Offset, OperationsModels
from sml2mqtt.sml_value.operations import SequenceOperation, OffsetOperation, VirtualMeterOperation
from sml2mqtt.sml_value.setup_operations import MAPPING, setup_operations


def assert_origins_equal(a, b):
    if a is types.UnionType and b is Union:
        return None
    if b is types.UnionType and a is Union:
        return None

    assert a is b


def remove_annotated(obj):
    ret = []
    for sub in get_args(obj):
        if get_origin(sub) is Annotated:
            sub = get_args(sub)[0]
        ret.append(sub)
    return ret


@pytest.mark.parametrize(('config_model', 'operation'), tuple(MAPPING.items()))
def test_field_to_init(config_model, operation):
    config_model.model_rebuild()

    sig_o = inspect.signature(operation)
    params = sig_o.parameters

    if list(params) == ['model']:
        return None

    for cfg_name, cfg_field in config_model.model_fields.items():
        assert cfg_name in params
        param = params[cfg_name]

        if origin_cfg := get_origin(cfg_field.annotation):
            origin_op = get_origin(param.annotation)
            assert_origins_equal(origin_cfg, origin_op)

            args_cfg = remove_annotated(cfg_field.annotation)
            args_op = remove_annotated(param.annotation)
            assert args_cfg == args_op

        else:
            assert cfg_field.annotation == param.annotation


def test_all_models_in_mapping():
    if missing := set(OperationsModels) - set(MAPPING):
        msg = f'Missing in OperationsModels: {", ".join(m.__name__ for m in missing)}'
        raise ValueError(msg)

    if missing := set(MAPPING) - set(OperationsModels):
        msg = f'Missing in MAPPING: {", ".join(m.__name__ for m in missing)}'
        raise ValueError(msg)


def test_simple():
    cfg = Sequence(sequence=[
        Offset(offset=5)
    ])

    o = SequenceOperation()

    setup_operations(o, cfg)

    assert list(o.describe()) == [
        '- Sequence:',
        '  - Offset: 5',
    ]


def test_virtual_meter():

    cfg = Sequence(sequence=[
        {'start now': True, 'times': ['02:00'], 'days': ['mon', 6]},
    ])

    o = SequenceOperation()

    setup_operations(o, cfg)

    assert len(o.operations) == 1

    o = o.operations[0]
    assert isinstance(o, VirtualMeterOperation)
    assert o.dt_finder.times == (time(2, 0), )
    assert o.dt_finder.days == (6, )
    assert o.dt_finder.dows == (1, )


def test_complex():
    cfg = Sequence(sequence=[
        {'offset': 5},
        {'or': [{'offset': 5}, {'factor': 3}]}
    ])

    o = SequenceOperation()

    setup_operations(o, cfg)

    assert list(o.describe()) == [
        '- Sequence:',
        '  - Offset: 5',
        '  - Or:',
        '    - Offset: 5',
        '    - Factor: 3'
    ]
