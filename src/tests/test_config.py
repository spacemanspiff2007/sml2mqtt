import pytest
from pydantic import ValidationError

from sml2mqtt.config.config import SmlValueConfig


def test_err_msg():

    with pytest.raises(ValidationError) as e:
        SmlValueConfig(transformations=[{'factor': 1, 'offset': 2}])

    assert str(e.value) == \
        '1 validation error for SmlValueConfig\n' \
        'transformations\n' \
        '  Only one entry allowed! Got 2: factor, offset (type=value_error)'
