import pytest
from pydantic import ValidationError

from sml2mqtt.config import cleanup_validation_errors
from sml2mqtt.config.config import SmlValueConfig


def test_err_msg():

    with pytest.raises(ValidationError) as e:
        SmlValueConfig.model_validate({
            'obis': '00112233445566',
            'mqtt': {'topic': 'OBIS'},
            'operations': [{'factor': 1, 'offset': 2}]
        })

    assert str(e.value) == \
        '1 validation error for SmlValueConfig\n' \
        'operations.0\n' \
        "  Invalid key names [type=invalid_key_names, input_value={'factor': 1, 'offset': 2}, input_type=dict]"


def test_error_message():

    with pytest.raises(ValidationError) as e:
        SmlValueConfig.model_validate({
            'obis': '00112233445566',
            'mqtt': {'topic': 'OBIS'},
            'operations': [
                {'negative on energy meter status': True},
                {'factor': 3}, {'offset': 100}, {'round': 2},
                {'or': [{'change filvter': True}, {'heartbeat action': 120}]}
            ]
        })

    assert '\n' + cleanup_validation_errors(str(e.value)) == '''
1 validation error for SmlValueConfig
operations.4.or.0
  Invalid key names [type=invalid_key_names, input_value={'change filvter': True}, input_type=dict]'''
