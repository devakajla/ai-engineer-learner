from solution import clamp_temperature


def test_examples():
    assert clamp_temperature(0.7) == 0.7
    assert clamp_temperature(-1) == 0.0
    assert clamp_temperature(5) == 2.0
    assert clamp_temperature(1) == 1.0


def test_edges():
    assert clamp_temperature(0) == 0.0
    assert clamp_temperature(2) == 2.0
    assert clamp_temperature(-0.01) == 0.0
    assert clamp_temperature(2.01) == 2.0


def test_returns_float():
    for value in (1, 0, 2, -3, 9, 0.5):
        assert isinstance(clamp_temperature(value), float), f"clamp_temperature({value}) must return a float"
