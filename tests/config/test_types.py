from __future__ import annotations

from datetime import timedelta

from pydantic import BaseModel

from sml2mqtt.config.types import ObisHex  # noqa: TCH001
from sml2mqtt.const import DurationType  # noqa: TCH001


def test_obis():
    class TestObis(BaseModel):
        value: ObisHex

    assert TestObis.model_validate({'value': '0100000009ff'}).value == '0100000009ff'
    assert TestObis.model_validate({'value': '0100000009FF'}).value == '0100000009ff'
    assert TestObis.model_validate({'value': '0100000009FF  '}).value == '0100000009ff'


def test_duration():
    class TestObis(BaseModel):
        value: DurationType

    assert TestObis.model_validate({'value': 0}).value == 0
    assert TestObis.model_validate({'value': 13.5}).value == 13.5
    assert TestObis.model_validate({'value': '01:00'}).value == timedelta(hours=1)
