import random
from solution import subsets_with_sum


def brute(nums, k):
    n = len(nums)
    out = []
    for mask in range(1 << n):
        sub = [nums[i] for i in range(n) if mask >> i & 1]
        if sum(sub) == k and sub:
            out.append(sub)
    return sorted(out)


def test_examples():
    assert subsets_with_sum([1, 2, 3, 4], 5) == [[1, 4], [2, 3]]
    assert subsets_with_sum([2, 4], 3) == []


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        nums = rng.sample(range(1, 9), rng.randint(0, 6))
        k = rng.randint(1, 15)
        assert subsets_with_sum(list(nums), k) == brute(nums, k), f"{nums}, {k}"
