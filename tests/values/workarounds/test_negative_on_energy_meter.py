from typing import Tuple

from smllib.sml import SmlListEntry

from sml2mqtt.value.workarounds import NegativeOnEnergyMeterStatus


def get_entries() -> Tuple[SmlListEntry, SmlListEntry]:

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

    return power, energy


def test_make_negative():

    wk = NegativeOnEnergyMeterStatus(True)

    power, energy = get_entries()
    assert energy.status == 418

    wk.fix(power, {power.obis: power, energy.obis: energy})

    assert power.value == -41890
    assert power.obis == '01000f0700ff'
    assert power.unit == 27
    assert power.scaler == -1


def test_keep_positive():

    wk = NegativeOnEnergyMeterStatus(True)

    power, energy = get_entries()
    energy.status = 0x182
    assert energy.status == 386

    wk.fix(power, {power.obis: power, energy.obis: energy})

    assert power.value == 41890
    assert power.obis == '01000f0700ff'
    assert power.unit == 27
    assert power.scaler == -1
