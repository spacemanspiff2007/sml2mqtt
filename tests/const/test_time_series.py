from sml2mqtt.const import TimeSeries


def test_time_series_boundaries() -> None:

    for wait_for_data in (True, False):
        t = TimeSeries(10, wait_for_data=wait_for_data)
        t.add_value(1, 0)
        t.add_value(2, 10)
        assert list(t.get_values()) == [1, 2]
        assert t.get_value_duration(10) == [(1, 10), (2, 0)]
        assert t.is_full

        t.add_value(3, 20)
        assert list(t.get_values()) == [2, 3]
        assert t.get_value_duration(20) == [(2, 10), (3, 0)]
        assert t.is_full

        t.add_value(4, 30)
        assert list(t.get_values()) == [3, 4]
        assert t.get_value_duration(30) == [(3, 10), (4, 0)]
        assert t.is_full


def test_time_series() -> None:
    t = TimeSeries(10)

    t.add_value(1, 3)
    t.add_value(2, 10)
    assert list(t.get_values()) == [1, 2]
    assert t.get_value_duration(10) == [(1, 7), (2, 0)]

    t.add_value(3, 15)
    assert list(t.get_values()) == [1, 2, 3]
    assert t.get_value_duration(15) == [(1, 5), (2, 5), (3, 0)]

    t.add_value(4, 17)
    assert list(t.get_values()) == [1, 2, 3, 4]
    assert t.get_value_duration(17) == [(1, 3), (2, 5), (3, 2), (4, 0)]

    t.add_value(5, 20)
    assert list(t.get_values()) == [2, 3, 4, 5]
    assert t.get_value_duration(20) == [(2, 5), (3, 2), (4, 3), (5, 0)]


def test_time_series_start() -> None:
    t = TimeSeries(10, wait_for_data=False)

    for _ in range(2):
        assert t.get_values() is None
        assert t.get_value_duration(0) is None

        t.add_value(1, 3)
        assert list(t.get_values()) == [1]
        assert t.get_value_duration(3) == [(1, 0)]

        t.add_value(None, 7)
        assert t.get_value_duration(7) == [(1, 4)]

        t.add_value(None, 13)
        assert t.get_value_duration(13) == [(1, 10)]

        t.add_value(None, 100)
        assert t.get_value_duration(100) == [(1, 10)]

        t.add_value(2, 200)
        assert list(t.get_values()) == [1, 2]
        assert t.get_value_duration(200) == [(1, 10), (2, 0)]

        t.clear()


def test_time_series_start_wait_for_data() -> None:
    t = TimeSeries(10, wait_for_data=True)

    for _ in range(2):
        assert t.get_values() is None
        assert t.get_value_duration(0) is None

        t.add_value(1, 3)
        assert t.get_values() is None
        assert t.get_value_duration(3) is None

        t.add_value(None, 7)
        assert t.get_value_duration(7) is None

        t.add_value(None, 13)
        assert t.get_value_duration(13) == [(1, 10)]

        t.add_value(None, 100)
        assert t.get_value_duration(100) == [(1, 10)]

        t.add_value(2, 200)
        assert list(t.get_values()) == [1, 2]
        assert t.get_value_duration(200) == [(1, 10), (2, 0)]

        t.clear()
