from sml2mqtt.config.operations import DeltaFilter


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
