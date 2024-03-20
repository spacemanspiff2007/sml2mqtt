import re
from collections.abc import Iterable

from sml2mqtt.sml_value.base import ValueOperationBase


RE_ID = re.compile(r' at 0x[0-f]{6,}>')


def check_operation_repr(obj: ValueOperationBase, *values):
    repr_str = RE_ID.sub('', repr(obj))

    class_name = obj.__class__.__name__
    for suffix in ('Operation', 'Filter'):
        class_name = class_name.removesuffix(suffix)

    values_str = ' '.join(values)
    if values_str:
        values_str = ': ' + values_str

    target = f'<{class_name:s}{values_str:s}'

    assert target == repr_str, f'\n{target}\n{repr_str}'


def check_description(obj: ValueOperationBase, value: str | Iterable[str]):
    desc = list(obj.describe())
    desc_text = '\n'.join(desc)
    if 'filter' in desc_text.lower():
        assert 'Filter' in desc_text, desc_text

    value = [value] if isinstance(value, str) else list(value)

    assert desc == value, f'\n{desc}\n{value}'
