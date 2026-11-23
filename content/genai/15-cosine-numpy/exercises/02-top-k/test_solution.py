import pytest

from solution import top_k

M = [[1, 0], [0, 1], [1, 1]]


def test_examples():
    result = top_k([1, 0], M, 2)
    assert [i for i, _ in result] == [0, 2]
    assert result[0][1] == pytest.approx(1.0)
    assert result[1][1] == pytest.approx(0.7071067811865475)
    assert [i for i, _ in top_k([1, 0], M, 10)] == [0, 2, 1]
    assert top_k([1, 0], [], 3) == []


def test_ties_lower_index_first():
    same = [[1, 0], [2, 0], [3, 0]]
    assert [i for i, _ in top_k([1, 0], same, 3)] == [0, 1, 2]


def test_zero_rows_and_query():
    result = top_k([1, 0], [[0, 0], [1, 0]], 2)
    assert [i for i, _ in result] == [1, 0]
    assert result[1][1] == 0.0
    assert all(score == 0.0 for _, score in top_k([0, 0], M, 3))


def test_k_edges_and_types():
    assert top_k([1, 0], M, 0) == []
    assert top_k([1, 0], M, -1) == []
    i, score = top_k([1, 0], M, 1)[0]
    assert type(i) is int and type(score) is float
