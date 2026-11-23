import pytest

from solution import cosine_similarity


def test_examples():
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(0.7071067811865475)
    assert cosine_similarity([1, 1], [10, 10]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_opposite_and_scale():
    assert cosine_similarity([1, 2], [-1, -2]) == pytest.approx(-1.0)
    assert cosine_similarity([2, 0, 0], [5, 0, 0]) == pytest.approx(1.0), "length must not matter"


def test_zero_vector():
    assert cosine_similarity([0, 0], [1, 2]) == 0.0
    assert cosine_similarity([1, 2], [0, 0]) == 0.0
    assert cosine_similarity([0, 0], [0, 0]) == 0.0


def test_return_type_and_length_check():
    result = cosine_similarity([1, 2], [3, 4])
    assert type(result) is float, "return a plain Python float"
    with pytest.raises(ValueError, match="vectors must have the same length"):
        cosine_similarity([1, 2], [1, 2, 3])
