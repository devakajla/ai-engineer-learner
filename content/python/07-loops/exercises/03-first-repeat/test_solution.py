from solution import first_repeat


def test_examples():
    assert first_repeat([3, 1, 4, 1, 5, 3]) == 1
    assert first_repeat([1, 2, 3]) is None


def test_more():
    assert first_repeat([]) is None
    assert first_repeat(["a", "b", "a"]) == "a"
    assert first_repeat([7, 7, 7]) == 7
    assert first_repeat([1, 2, 2, 1]) == 2, "2 repeats before 1 does"
