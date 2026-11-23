import itertools

import pytest

from solution import chunked


def test_basic():
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(chunked([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]
    assert list(chunked([], 3)) == []


def test_generator_input():
    assert list(chunked((x for x in range(5)), 4)) == [[0, 1, 2, 3], [4]]


def test_infinite_is_lazy():
    g = chunked(itertools.count(), 3)
    assert next(g) == [0, 1, 2]
    assert next(g) == [3, 4, 5]


def test_bad_size_raises_immediately():
    with pytest.raises(ValueError):
        chunked([1, 2], 0)
