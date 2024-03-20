from sml2mqtt.sml_value.operations.time_series import TimeSeries


def test_time_series(monotonic):
    t = TimeSeries(10)

    t.add_value(1, 5)

    monotonic.add(10)
    t.add_value(1, 10)

    assert list(t.get_values()) == [1, 1]
