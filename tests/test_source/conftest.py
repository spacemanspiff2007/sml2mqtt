from unittest.mock import Mock

import pytest

from sml2mqtt.const import DeviceProto


class DeviceMock(DeviceProto):

    def __init__(self):
        self.on_source_data = Mock()
        self.on_source_failed = Mock()
        self.on_error = Mock()

    @property
    def name(self) -> str:
        return f'DeviceMock at 0x{id(self):x}'


@pytest.fixture()
def device_mock() -> DeviceMock:
    m = DeviceMock()
    m.on_source_data.assert_not_called()
    m.on_source_failed.assert_not_called()
    m.on_error.assert_not_called()

    return m
