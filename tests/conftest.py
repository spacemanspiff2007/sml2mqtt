import logging
import traceback
from typing import TYPE_CHECKING

import pytest
from helper import PatchedSmlStreamReader
from tests.sml_data import (
    sml_data_1,
    sml_data_1_analyze,
    sml_frame_1,
    sml_frame_1_analyze,
    sml_frame_1_values,
    sml_frame_2,
    sml_frame_2_analyze,
    sml_frame_2_values,
)

import sml2mqtt.const.task as task_module
import sml2mqtt.mqtt.mqtt_obj
from sml2mqtt import CMD_ARGS
from sml2mqtt.runtime import shutdown as shutdown_module
from sml2mqtt.sml_device import sml_device as sml_device_module


if TYPE_CHECKING:
    sml_data_1         = sml_data_1
    sml_data_1_analyze = sml_data_1_analyze

    sml_frame_1         = sml_frame_1
    sml_frame_1_values  = sml_frame_1_values
    sml_frame_1_analyze = sml_frame_1_analyze

    sml_frame_2         = sml_frame_2
    sml_frame_2_values  = sml_frame_2_values
    sml_frame_2_analyze = sml_frame_2_analyze


class PatchedMonotonic:
    def __init__(self):
        self._now: int | float = 0
        self._mp = pytest.MonkeyPatch()

    def _get_monotonic(self):
        return self._now

    def patch_name(self, target: str):
        self._mp.setattr(target, self._get_monotonic)

    def patch(self, target: str | object, name: str | object):
        self._mp.setattr(target, name, value=self._get_monotonic)

    def undo(self):
        self._mp.undo()

    def add(self, secs: float):
        self._now += secs

    def set(self, secs: float):
        self._now = secs


@pytest.fixture()
def monotonic():
    p = PatchedMonotonic()

    p.patch_name('sml2mqtt.sml_value.operations.filter.monotonic')
    p.patch_name('sml2mqtt.sml_value.operations.time_series.monotonic')
    p.patch_name('sml2mqtt.sml_value.operations.actions.monotonic')

    try:
        yield p
    finally:
        p.undo()


@pytest.fixture()
def no_mqtt(monkeypatch):

    pub_list = []

    def pub_func(topic: str, value, qos: int, retain: bool):
        pub_list.append((topic, value, qos, retain))

    monkeypatch.setattr(sml2mqtt.mqtt.mqtt_obj, 'pub_func', pub_func)
    return pub_list


@pytest.fixture()
def stream_reader(monkeypatch):
    r = PatchedSmlStreamReader()
    monkeypatch.setattr(sml_device_module, 'SmlStreamReader', lambda: r)
    return r


@pytest.fixture(autouse=True)
def check_no_logged_error(caplog, request):
    caplog.set_level(logging.DEBUG)

    yield None

    all_levels = set(logging._levelToName)
    fail_on_default = {lvl for lvl in all_levels if lvl >= logging.WARNING}
    fail_on = fail_on_default.copy()

    markers = request.node.own_markers
    for marker in markers:
        if marker.name == 'ignore_log_errors':
            fail_on.discard(logging.ERROR)
        elif marker.name == 'ignore_log_warnings':
            fail_on.discard(logging.WARNING)

    msgs = []
    for fail_lvls, phase in ((fail_on_default, 'setup'), (fail_on, 'call'), (fail_on_default, 'teardown')):
        for record in caplog.get_records(phase):
            if record.levelno not in all_levels:
                msg = f'Unknown log level: {record.levelno}! Supported: {", ".join(all_levels)}'
                raise ValueError(msg)

            if record.levelno in fail_lvls:
                msgs.append(f'{record.name:20s} | {record.levelname:7} | {record.getMessage():s}')

    if msgs:
        pytest.fail(reason='Error in log:\n' + '\n'.join(msgs))


@pytest.fixture(autouse=True)
def _wrap_all_tasks(monkeypatch):

    async def wrapped_future(coro):
        try:
            return await coro
        except Exception:
            for line in traceback.format_exc().splitlines():
                logging.getLogger('task_wrap').error(line)
            raise

    original = task_module.asyncio_create_task

    def create_task(coro, *, name=None):
        return original(wrapped_future(coro), name=name)

    monkeypatch.setattr(task_module, 'create_task', create_task)


@pytest.fixture()
def arg_analyze(monkeypatch):
    monkeypatch.setattr(CMD_ARGS, 'analyze', True)
    sml2mqtt.mqtt.patch_analyze()

    yield None

    module = sml2mqtt.mqtt.mqtt_obj
    assert hasattr(module, 'pub_func')
    module.pub_func = module.publish


@pytest.fixture(autouse=True)
async def _patch_shutdown(monkeypatch):
    objs = ()
    monkeypatch.setattr(shutdown_module, 'SHUTDOWN_OBJS', objs)

    yield

    for obj in objs:
        await obj.do()
