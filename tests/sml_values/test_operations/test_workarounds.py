from smllib.sml import SmlListEntry
from tests.sml_values.test_operations.helper import check_operation_repr

from sml2mqtt.const import SmlFrameValues
from sml2mqtt.sml_value.base import SmlValueInfo
from sml2mqtt.sml_value.operations import NegativeOnEnergyMeterWorkaroundOperation


def get_info() -> SmlValueInfo:

    power = SmlListEntry()
    power.obis = '01000f0700ff'
    power.unit = 27
    power.scaler = -1
    power.value = 41890

    energy = SmlListEntry()
    energy.obis = '0100010800ff'
    energy.status = 0x1A2
    energy.unit = 30
    energy.scaler = -1
    energy.value = 300371964

    return SmlValueInfo(power, SmlFrameValues.create(0, [power, energy]), 0)


def test_repr():
    o = NegativeOnEnergyMeterWorkaroundOperation()
    check_operation_repr(o, '0100010800ff')


def test_make_negative():
    o = NegativeOnEnergyMeterWorkaroundOperation()

    info = get_info()
    value = info.value.get_value()

    assert o.process_value(value, info) == -4189.0


def test_keep_positive():
    o = NegativeOnEnergyMeterWorkaroundOperation()

    info = get_info()
    value = info.value.get_value()

    energy = info.frame.get_value('0100010800ff')
    energy.status = 0x182

    assert o.process_value(value, info) == 4189.0
