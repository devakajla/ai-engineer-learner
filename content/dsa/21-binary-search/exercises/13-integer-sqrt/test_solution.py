from math import isqrt
from solution import int_sqrt


def test_examples():
    assert int_sqrt(8) == 2
    assert int_sqrt(16) == 4


def test_edges():
    assert int_sqrt(0) == 0
    assert int_sqrt(1) == 1
    assert int_sqrt(2) == 1
    assert int_sqrt(10 ** 18) == 10 ** 9, "must be fast"
    assert int_sqrt(10 ** 18 - 1) == 10 ** 9 - 1


def test_many():
    for x in range(0, 300):
        assert int_sqrt(x) == isqrt(x), f"x = {x}"
