from solution import calculate


def test_examples():
    assert calculate(6, "+", 2) == 8
    assert calculate(6, "/", 0) is None
    assert calculate(5, "neg") == -5


def test_more():
    assert calculate(6, "-", 10) == -4
    assert calculate(3, "*", 4) == 12
    assert calculate(7, "/", 2) == 3.5
    assert calculate(1, "%", 2) is None, "unknown operator"
    assert calculate(0, "neg") == 0
