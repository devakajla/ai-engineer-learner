from solution import first_repeat


def test_examples():
    assert first_repeat([3, 1, 4, 1, 3]) == 1
    assert first_repeat([1, 2, 3]) is None


def test_more():
    assert first_repeat([]) is None
    assert first_repeat([2, 2]) == 2
    assert first_repeat(["a", "b", "b", "a"]) == "b"
    assert first_repeat([5, 6, 7, 6, 5, 5]) == 6
