import sml2mqtt.value.refresh_marker as marker_package


def test_rest_code(monkeypatch):

    timestamp = 0
    monkeypatch.setattr(marker_package, 'monotonic', lambda: timestamp)

    marker = marker_package.RefreshMarker(5)

    timestamp = 1
    assert marker.required(1)
    assert marker.required(2)
    marker.done(1)
    assert not marker.required(1)
    assert marker.required(2)

    timestamp = 6
    assert marker.required(1)
    assert marker.required(2)
    marker.done(2)
    assert marker.required(1)
    assert not marker.required(2)
