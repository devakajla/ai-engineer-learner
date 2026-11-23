from solution import reciprocal_rank


def test_first():
    assert reciprocal_rank(["a"], ["a", "x"]) == 1.0


def test_third():
    assert abs(reciprocal_rank(["a"], ["x", "y", "a"]) - 1 / 3) < 1e-9


def test_first_of_many_expected_counts():
    assert reciprocal_rank(["a", "b"], ["x", "b", "a"]) == 0.5


def test_none():
    assert reciprocal_rank(["a"], ["x"]) == 0.0
    assert reciprocal_rank(["a"], []) == 0.0
    assert reciprocal_rank([], ["a"]) == 0.0
