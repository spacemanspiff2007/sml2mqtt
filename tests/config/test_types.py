from __future__ import annotations

from pydantic import BaseModel

from sml2mqtt.config.types import ObisHex  # noqa: TCH001


def test_obis():
    class TestObis(BaseModel):
        value: ObisHex

    assert TestObis.model_validate({'value': '0100000009ff'}).value == '0100000009ff'
    assert TestObis.model_validate({'value': '0100000009FF'}).value == '0100000009ff'
    assert TestObis.model_validate({'value': '0100000009FF  '}).value == '0100000009ff'
