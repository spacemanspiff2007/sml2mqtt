from unittest.mock import Mock

from smllib.sml import SmlListEntry

from sml2mqtt.sml_value import SmlValue
from sml2mqtt.sml_value.filter import RefreshEvery
from sml2mqtt.sml_value.transformations import RoundTransformation


def test_round():
    r = RoundTransformation(0)
    assert r.process(1.11) == 1
    assert isinstance(r.process(1.11), int)
    assert str(r) == '<Round: 0>'

    r = RoundTransformation(1)
    assert r.process(1.11) == 1.1
    assert isinstance(r.process(1.11), float)
    assert str(r) == '<Round: 1>'


def test_round_call():
    m = Mock()
    v = SmlValue('device', 'obis', m, [], [RoundTransformation(0)], [RefreshEvery(120)])

    power = SmlListEntry()
    power.obis = '01000f0700ff'
    power.unit = 27
    power.scaler = -1
    power.value = 41891

    v.set_value(power, {})

    m.publish.assert_called_once_with(4189)
