from solution import dedupe


def test_examples():
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe(["a", "a", "a"]) == ["a"]


def test_more():
    assert dedupe([]) == []
    assert dedupe([1, 2, 3]) == [1, 2, 3]
    original = [1, 1, 2]
    result = dedupe(original)
    assert original == [1, 1, 2], "do not change the input list"
    assert result is not original
