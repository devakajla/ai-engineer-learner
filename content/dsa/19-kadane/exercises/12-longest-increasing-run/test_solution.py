import random
from solution import longest_increasing_run


def brute(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            part = nums[i:j + 1]
            if all(b > a for a, b in zip(part, part[1:])):
                best = max(best, len(part))
    return best


def test_examples():
    assert longest_increasing_run([1, 3, 5, 4, 7]) == 3
    assert longest_increasing_run([2, 2, 2]) == 1


def test_edges():
    assert longest_increasing_run([]) == 0
    assert longest_increasing_run([9]) == 1
    assert longest_increasing_run([1, 2, 3, 4]) == 4


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 10))]
        assert longest_increasing_run(nums) == brute(nums), f"{nums}"
