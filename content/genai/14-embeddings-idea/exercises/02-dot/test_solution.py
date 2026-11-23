import pytest

from solution import dot


def test_examples():
    assert dot([1, 2, 3], [4, 5, 6]) == 32
    assert dot([1, 0], [0, 1]) == 0
    assert dot([], []) == 0


def test_floats_and_negatives():
    assert dot([0.5, 0.5], [2, 4]) == 3.0
    assert dot([1, -1], [1, 1]) == 0
    assert dot([-2, 3], [4, 5]) == 7


def test_length_mismatch():
    with pytest.raises(ValueError) as info:
        dot([1, 2], [1, 2, 3])
    assert str(info.value) == "vectors must have the same length"
    with pytest.raises(ValueError):
        dot([1, 2, 3], [1])
