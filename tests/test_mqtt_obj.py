from sml2mqtt.mqtt import MqttObj


def test_topmost(monkeypatch):
    parent = MqttObj('base', 2, True).update()

    assert parent.topic == 'base'
    assert parent.qos == 2
    assert parent.retain is True

    parent.set_topic('base_new')
    assert parent.topic == 'base_new'
    assert parent.qos == 2
    assert parent.retain is True


def test_child_change(monkeypatch):
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
