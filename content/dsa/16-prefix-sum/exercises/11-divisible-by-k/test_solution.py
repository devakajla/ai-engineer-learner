import random
from solution import divisible_by_k


def brute(nums, k):
    return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) % k == 0)


def test_examples():
    assert divisible_by_k([4, 5, 0, -2, -3, 1], 5) == 7
    assert divisible_by_k([5], 9) == 0


def test_edges():
    assert divisible_by_k([], 3) == 0
    assert divisible_by_k([3], 3) == 1
    assert divisible_by_k([1, 2, 3], 1) == 6, "everything is divisible by 1"


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        nums = [rng.randint(-7, 7) for _ in range(rng.randint(0, 10))]
        k = rng.randint(1, 6)
        assert divisible_by_k(nums, k) == brute(nums, k), f"{nums}, {k}"
