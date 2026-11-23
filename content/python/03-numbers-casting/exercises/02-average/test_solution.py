from solution import average


def test_examples():
    assert average(1, 2, 3) == 2.0
    assert average(1, 2, 2) == 1.67
    assert average(0.1, 0.2, 0.3) == 0.2


def test_negative():
    assert average(-1, -2, -4) == -2.33


def test_returns_float():
    assert isinstance(average(2, 2, 2), float), "true division / gives a float"
