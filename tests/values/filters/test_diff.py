from sml2mqtt.sml_value.filter import DiffAbsFilter, DiffPercFilter


def test_abs():
    f = DiffAbsFilter(5)
    assert f.required(0)
    f.done(0)

    assert not f.required(1)
    assert not f.required(4.999999)
    assert f.required(5)

    assert not f.required(-1)
    assert not f.required(-4.999999)
    assert f.required(-5)


def test_perc():
    f = DiffPercFilter(5)
    assert f.required(100)
    f.done(100)

    assert not f.required(100)
    assert not f.required(104.999999)
    assert f.required(105)

    assert not f.required(99)
    assert not f.required(95.0000001)
    assert f.required(95)
