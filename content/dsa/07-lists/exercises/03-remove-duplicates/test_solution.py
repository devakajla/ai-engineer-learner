from solution import remove_duplicates


def test_examples():
    assert remove_duplicates([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert remove_duplicates([]) == []


def test_more():
    assert remove_duplicates([1, 1, 1]) == [1]
    assert remove_duplicates(["a", "b", "a"]) == ["a", "b"]
    assert remove_duplicates([1, 2, 3]) == [1, 2, 3]
