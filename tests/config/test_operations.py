import pytest
from pydantic import ValidationError

from sml2mqtt.config.device import SmlValueConfig
from sml2mqtt.config.operations import DeltaFilter, cleanup_validation_errors


def test_delta_filter():
    f = DeltaFilter.model_validate({'delta filter': 3})
    assert f.is_percent is False
    assert f.delta == 3

    f = DeltaFilter.model_validate({'delta filter': -3.33})
    assert f.is_percent is False
    assert f.delta == -3.33

    f = DeltaFilter.model_validate({'delta filter': '3 %'})
    assert f.is_percent is True
    assert f.delta == 3

    f = DeltaFilter.model_validate({'delta filter': '33%'})
    assert f.is_percent is True
    assert f.delta == 33

    f = DeltaFilter.model_validate({'delta filter': '-3.33 %'})
    assert f.is_percent is True
    assert f.delta == -3.33


def test_error_message():

    with pytest.raises(ValidationError) as e:
        SmlValueConfig.model_validate({
            'obis': '00112233445566',
            'mqtt': {'topic': 'OBIS'},
            'operations': [
                {'negative on energy meter status': True},
                {'factor': 3}, {'offset': 100}, {'round': 2},
                {'or': [{'change filvter': True}, {'heartbeat filter': 120}]}
            ]
        })

    assert '\n' + cleanup_validation_errors(str(e.value)) == '''
1 validation error for SmlValueConfig
operations.4.or.0
  Invalid key names [type=invalid_key_names, input_value={'change filvter': True}, input_type=dict]'''
