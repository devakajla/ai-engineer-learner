from solution import running_sum


def test_examples():
    assert running_sum([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert running_sum([]) == []


def test_more():
    assert running_sum([5]) == [5]
    assert running_sum([-1, 1, -1]) == [-1, 0, -1]
    original = [1, 2]
    running_sum(original)
    assert original == [1, 2], "do not change the input"
