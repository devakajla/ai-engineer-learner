from solution import two_sum


def test_examples():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 2, 4], 6) == (1, 2)
    assert two_sum([1, 2], 10) is None


def test_more():
    assert two_sum([3, 3], 6) == (0, 1), "the same value can be used twice at different indexes"
    assert two_sum([], 1) is None
    assert two_sum([5], 10) is None, "one item cannot pair with itself"
    assert two_sum([-1, -2, -3, -4], -6) == (1, 3)


def test_large_input_is_fast():
    nums = list(range(200_000))
    assert two_sum(nums, 399_997) == (199_998, 199_999)
