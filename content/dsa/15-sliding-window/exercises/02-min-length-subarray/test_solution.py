import random
from solution import min_len_subarray


def brute(nums, target):
    best = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s >= target:
                if best == 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def test_examples():
    assert min_len_subarray([2, 3, 1, 2, 4, 3], 7) == 2
    assert min_len_subarray([1, 1, 1], 10) == 0


def test_edges():
    assert min_len_subarray([], 3) == 0
    assert min_len_subarray([9], 9) == 1
    assert min_len_subarray([1, 2, 3, 4, 5], 15) == 5, "need everything"
    assert min_len_subarray([1, 4, 4], 4) == 1


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(1, 8) for _ in range(rng.randint(0, 12))]
        target = rng.randint(1, 30)
        assert min_len_subarray(nums, target) == brute(nums, target), f"{nums}, {target}"
