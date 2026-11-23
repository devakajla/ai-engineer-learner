from solution import second_largest


def test_examples():
    assert second_largest([4, 9, 2, 9, 7]) == 7
    assert second_largest([5, 5]) is None


def test_more():
    assert second_largest([]) is None
    assert second_largest([1]) is None
    assert second_largest([1, 2]) == 1
    assert second_largest([-1, -5, -3]) == -3
    nums = [3, 1, 2]
    second_largest(nums)
    assert nums == [3, 1, 2], "do not change the input list"
