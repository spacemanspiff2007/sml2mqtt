import inspect
import types
from datetime import time
from typing import Annotated, Union, get_args, get_origin

import pytest
from pydantic import BaseModel

from sml2mqtt.config.operations import Sequence, Offset, OperationsModels
import sml2mqtt.config.operations as operations_module
from sml2mqtt.sml_value.operations import SequenceOperation, OffsetOperation, VirtualMeterOperation
from sml2mqtt.sml_value.setup_operations import MAPPING, setup_operations, get_kwargs_names


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


def get_kwargs_return_annotation(obj) -> None | str:
    name = 'get_kwargs'
    if not hasattr(obj, name):
        raise ValueError()

    if (sig := inspect.signature(getattr(obj, name)).return_annotation) == 'None':
        return None
    return sig


@pytest.mark.parametrize(('config_model', 'operation'), tuple(MAPPING.items()))
def test_field_to_init(config_model: type[BaseModel], operation: callable):
    config_model.model_rebuild()

    sig_o = inspect.signature(operation)
    params = sig_o.parameters

    config_provides = {}

    if kwarg_func_names := get_kwargs_names(config_model):
        for kwarg_func_name in kwarg_func_names:
            return_annotation = inspect.signature(getattr(config_model, kwarg_func_name)).return_annotation
            typed_dict = getattr(operations_module, return_annotation)
            annotations = inspect.get_annotations(typed_dict)

            for name, fwd_ref in annotations.items():
                ref_type = fwd_ref._evaluate(vars(operations_module), {}, frozenset())
                assert name not in config_provides, config_provides
                config_provides[name] = ref_type
    else:
        for _cfg_name, _cfg_field in config_model.model_fields.items():
            config_provides[_cfg_name] = _cfg_field.annotation

    for name, type_hint in config_provides.items():
        assert name in params
        param = params[name]

        if origin_cfg := get_origin(type_hint):
            origin_op = get_origin(param.annotation)
            assert_origins_equal(origin_cfg, origin_op)

            args_cfg = remove_annotated(type_hint)
            args_op = remove_annotated(param.annotation)
            assert args_cfg == args_op

        else:
            assert type_hint == param.annotation

    if missing := set(params) - set(config_provides):
        raise ValueError(f'The following arguments are missing for {operation.__name__}: {", ".join(missing)}')


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
        {'type': 'meter', 'start now': True, 'reset times': ['02:00'], 'reset days': ['mon', 6]},
    ])

    o = SequenceOperation()

    setup_operations(o, cfg)

    assert len(o.operations) == 1

    o = o.operations[0]
    assert isinstance(o, VirtualMeterOperation)
    assert o._dt_finder.times == (time(2, 0), )
    assert o._dt_finder.days == (6, )
    assert o._dt_finder.dows == (1, )


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
