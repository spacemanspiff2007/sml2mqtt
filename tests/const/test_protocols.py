import inspect
from typing import Protocol

import pytest

from sml2mqtt.const import DeviceProto
from sml2mqtt.sml_device import SmlDevice


def assert_signatures(a, b):
    sig_a = inspect.signature(a) if a is not None else a
    sig_b = inspect.signature(b) if b is not None else b
    assert sig_a == sig_b, f'\n  {sig_a}\n  {sig_b}\n'


@pytest.mark.parametrize(
    ('proto', 'cls'), [(DeviceProto, SmlDevice), ]
)
def test_protocols(proto: type[Protocol], cls: type):
    for name, proto_obj in inspect.getmembers(proto):
        if name.startswith('_'):
            continue

        class_obj = getattr(cls, name)

        if isinstance(class_obj, property):
            assert_signatures(proto_obj.fget, class_obj.fget)
            assert_signatures(proto_obj.fset, class_obj.fset)
            assert_signatures(proto_obj.fdel, class_obj.fdel)
        else:
            assert_signatures(proto_obj, class_obj)
