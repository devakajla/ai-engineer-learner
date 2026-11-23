from solution import clamp


def test_examples():
    assert clamp(5, 0, 10) == 5
    assert clamp(-3, 0, 10) == 0
    assert clamp(99, 0, 10) == 10


def test_edges():
    assert clamp(0, 0, 10) == 0, "x equals low"
    assert clamp(10, 0, 10) == 10, "x equals high"
    assert clamp(-5, -10, -1) == -5, "negative range"
    assert clamp(3, 3, 3) == 3, "low == high"
