import random
from solution import two_sum_less_than_k


def brute(nums, k):
    best = -1
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            s = nums[i] + nums[j]
            if s < k and s > best:
                best = s
    return best


def test_examples():
    assert two_sum_less_than_k([34, 23, 1, 24, 75, 33, 54, 8], 60) == 58
    assert two_sum_less_than_k([10, 20, 30], 15) == -1


def test_edges():
    assert two_sum_less_than_k([], 10) == -1
    assert two_sum_less_than_k([5], 10) == -1
    assert two_sum_less_than_k([1, 2], 3) == -1, "3 is not less than 3"
    assert two_sum_less_than_k([1, 2], 4) == 3
    assert two_sum_less_than_k([5, 3, 8], 9) == 8


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        nums = [rng.randint(1, 20) for _ in range(rng.randint(0, 9))]
        k = rng.randint(1, 30)
        assert two_sum_less_than_k(list(nums), k) == brute(nums, k), f"{nums}, {k}"
