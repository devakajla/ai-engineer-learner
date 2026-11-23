import random
from solution import count_subsets


def brute(nums, target):
    n = len(nums)
    return sum(1 for mask in range(1 << n) if sum(nums[i] for i in range(n) if mask >> i & 1) == target)


def test_examples():
    assert count_subsets([1, 2, 3], 3) == 2
    assert count_subsets([0, 0], 0) == 4


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(0, 8))]
        target = rng.randint(0, 12)
        assert count_subsets(list(nums), target) == brute(nums, target), f"{nums}, {target}"
