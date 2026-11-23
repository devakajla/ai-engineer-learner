from solution import recall_at_k


def test_half():
    assert recall_at_k(["a", "b"], ["x", "a", "y"], 3) == 0.5


def test_outside_top_k():
    assert recall_at_k(["a"], ["x", "a"], 1) == 0.0
    assert recall_at_k(["a"], ["x", "a"], 2) == 1.0


def test_all_found():
    assert recall_at_k(["a", "b"], ["b", "a"], 5) == 1.0


def test_empty_expected():
    assert recall_at_k([], ["x"], 3) == 1.0


def test_k_zero_and_no_results():
    assert recall_at_k(["a"], ["a"], 0) == 0.0
    assert recall_at_k(["a"], [], 3) == 0.0
