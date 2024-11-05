import pytest

from sml2mqtt.mqtt import MqttObj, check_for_duplicate_topics


def test_topmost(monkeypatch) -> None:
    parent = MqttObj('base', 2, True).update()

    assert parent.topic == 'base'
    assert parent.qos == 2
    assert parent.retain is True

    parent.set_topic('base_new')
    assert parent.topic == 'base_new'
    assert parent.qos == 2
    assert parent.retain is True


def test_prefix_empty(monkeypatch) -> None:
    parent = MqttObj('', 2, True).update()
    child = parent.create_child('child')

    assert (child.topic, child.qos, child.retain) == ('child', 2, True)


def test_child_change(monkeypatch) -> None:
    parent = MqttObj('base', 2, True).update()
    child = parent.create_child('child')

    assert (child.topic, child.qos, child.retain) == ('base/child', 2, True)

    # QOS overwrite
    child.cfg.qos = 0
    child.update()
    assert (child.topic, child.qos, child.retain) == ('base/child', 0, True)

    # Retain overwrite
    child.cfg.retain = False
    child.update()
    assert (child.topic, child.qos, child.retain) == ('base/child', 0, False)

    # Load defaults from parent again
    child.cfg.qos = None
    child.cfg.retain = None
    child.update()
    assert (child.topic, child.qos, child.retain) == ('base/child', 2, True)

    # Parent changes - should reflect now on child
    parent.cfg.qos = 0
    parent.cfg.retain = False
    parent.update()
    assert (child.topic, child.qos, child.retain) == ('base/child', 0, False)


@pytest.mark.ignore_log_warnings
def test_check_for_duplicate_messages(caplog) -> None:
    parent = MqttObj('base', 2, True).update()
    parent.create_child('child')
    parent.create_child('child')

    check_for_duplicate_topics(parent)

    msg = '\n'.join(x.msg for x in caplog.records)

    assert msg == 'Topic "base/child" is already configured!'
