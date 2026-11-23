import random
from solution import max_increasing_sum


def brute(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            part = nums[i:j + 1]
            if all(b > a for a, b in zip(part, part[1:])):
                best = max(best, sum(part))
    return best


def test_examples():
    assert max_increasing_sum([10, 20, 30, 5, 10, 50]) == 65
    assert max_increasing_sum([12, 17, 15, 13, 10, 11, 12]) == 33


def test_edges():
    assert max_increasing_sum([]) == 0
    assert max_increasing_sum([3, 2, 1]) == 3
    assert max_increasing_sum([5, 5]) == 5, "equal is not increasing"


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        nums = [rng.randint(1, 9) for _ in range(rng.randint(0, 10))]
        assert max_increasing_sum(nums) == brute(nums), f"{nums}"
