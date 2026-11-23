import random
from solution import longest_consecutive


def brute(nums):
    s = sorted(set(nums))
    best = cur = 0
    for i, x in enumerate(s):
        cur = cur + 1 if i and s[i - 1] == x - 1 else 1
        best = max(best, cur)
    return best


def test_examples():
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9


def test_edges():
    assert longest_consecutive([]) == 0
    assert longest_consecutive([5]) == 1
    assert longest_consecutive([1, 1, 1]) == 1, "duplicates do not extend a run"
    assert longest_consecutive([-2, -1, 0]) == 3


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 10))]
        assert longest_consecutive(nums) == brute(nums), f"{nums}"
