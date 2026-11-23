import math

from solution import circle_area


def test_examples():
    assert circle_area(1) == math.pi
    assert circle_area(0) == 0.0


def test_more():
    assert math.isclose(circle_area(2), 4 * math.pi)
    assert math.isclose(circle_area(2.5), 6.25 * math.pi)
