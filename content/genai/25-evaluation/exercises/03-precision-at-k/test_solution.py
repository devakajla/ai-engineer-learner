from solution import precision_at_k


def test_two_of_three():
    assert abs(precision_at_k(["a", "b"], ["a", "x", "b"], 3) - 2 / 3) < 1e-9


def test_fewer_results_than_k():
    assert precision_at_k(["a"], ["a"], 4) == 0.25


def test_only_top_k_counts():
    assert precision_at_k(["a"], ["x", "a"], 1) == 0.0


def test_zero_k():
    assert precision_at_k(["a"], ["a"], 0) == 0.0


def test_all_right():
    assert precision_at_k(["a", "b"], ["a", "b"], 2) == 1.0
