from solution import has_pair


def test_examples():
    assert has_pair([2, 7, 11, 15], 9) is True
    assert has_pair([3, 3], 6) is True
    assert has_pair([3], 6) is False


def test_edges():
    assert has_pair([], 0) is False
    assert has_pair([3, 4], 6) is False, "3 + 3 would reuse the same position"
    assert has_pair([-1, 5, 1], 0) is True
    assert has_pair([0, 0], 0) is True


def test_big_input_is_fast():
    nums = list(range(0, 60000, 2))          # all even numbers
    assert has_pair(nums, 59997) is False    # odd target: no pair
    assert has_pair(nums, 59998) is True
