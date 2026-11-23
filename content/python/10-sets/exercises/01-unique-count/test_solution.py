from solution import unique_count


def test_examples():
    assert unique_count([1, 2, 2, 3, 3, 3]) == 3
    assert unique_count([]) == 0


def test_more():
    assert unique_count(["a", "A", "a"]) == 2
    assert unique_count([5]) == 1
    assert unique_count([(1, 2), (1, 2), (2, 1)]) == 2
