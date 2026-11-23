import pytest

from solution import euclidean


def test_examples():
    assert euclidean([0, 0], [3, 4]) == 5.0
    assert euclidean([1, 2, 3], [1, 2, 3]) == 0.0
    assert euclidean([1], [4]) == 3.0


def test_symmetric_and_float():
    assert euclidean([1, 5], [4, 1]) == euclidean([4, 1], [1, 5]) == 5.0
    assert isinstance(euclidean([1], [1]), float), "return a float, even for distance 0"
    assert euclidean([1, 1], [2, 2]) == pytest.approx(2 ** 0.5)


def test_length_mismatch():
    with pytest.raises(ValueError, match="vectors must have the same length"):
        euclidean([1, 2], [1])
    assert euclidean([], []) == 0.0
