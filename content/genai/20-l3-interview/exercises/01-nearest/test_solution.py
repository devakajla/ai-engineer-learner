import pytest

from solution import nearest


def test_examples():
    result = nearest([1, 0], [[1, 0], [0, 1], [1, 1]], 2)
    assert [i for i, _ in result] == [0, 2]
    assert result[0][1] == pytest.approx(1.0) and result[1][1] == pytest.approx(0.7071067811865475)
    result = nearest([1, 0], [[0, 0], [2, 0]], 5)
    assert [i for i, _ in result] == [1, 0]
    assert result[1][1] == 0.0
    with pytest.raises(ValueError, match="dimension mismatch"):
        nearest([1, 0], [[1, 0, 0]], 1)


def test_ties_lower_index_first():
    assert [i for i, _ in nearest([1, 0], [[2, 0], [1, 0], [3, 0]], 3)] == [0, 1, 2]


def test_edges():
    assert nearest([1, 0], [], 3) == []
    assert nearest([1, 0], [[1, 0]], 0) == []
    assert nearest([1, 0], [[1, 0]], -2) == []
    assert nearest([0, 0], [[1, 0], [0, 1]], 2) == [(0, 0.0), (1, 0.0)]


def test_scores_are_floats_and_k_limits():
    result = nearest([1, 1], [[1, 1], [1, 0], [0, 1], [-1, -1]], 3)
    assert len(result) == 3 and all(type(score) is float for _, score in result)
    assert nearest([1, 1], [[1, 1], [-1, -1]], 2)[1][1] == pytest.approx(-1.0)
