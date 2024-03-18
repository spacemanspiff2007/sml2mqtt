import inspect
import types
from typing import Annotated, Union, get_args, get_origin

import pytest

from sml2mqtt.sml_value.setup_operations import MAPPING


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