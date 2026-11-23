import random
from solution import max_circular


def brute(nums):
    n = len(nums)
    best = None
    for start in range(n):
        for length in range(1, n + 1):
            s = sum(nums[(start + k) % n] for k in range(length))
            best = s if best is None else max(best, s)
    return best


def test_examples():
    assert max_circular([5, -3, 5]) == 10
    assert max_circular([-3, -2, -3]) == -2


def test_edges():
    assert max_circular([4]) == 4
    assert max_circular([1, -2, 3, -2]) == 3
    assert max_circular([3, -1, 2, -1]) == 4
    assert max_circular([2, 2, 2]) == 6, "take everything"


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(1, 8))]
        assert max_circular(nums) == brute(nums), f"{nums}"
