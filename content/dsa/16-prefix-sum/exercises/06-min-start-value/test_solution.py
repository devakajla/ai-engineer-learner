import random
from solution import min_start_value


def ok(start, nums):
    t = start
    for x in nums:
        t += x
        if t < 1:
            return False
    return True


def test_examples():
    assert min_start_value([-3, 2, -3, 4, 2]) == 5
    assert min_start_value([1, 2]) == 1


def test_edges():
    assert min_start_value([]) == 1
    assert min_start_value([-5]) == 6


def test_random():
    rng = random.Random(5)
    for _ in range(200):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 8))]
        s = 1
        while not ok(s, nums):
            s += 1
        assert min_start_value(nums) == s, f"{nums}"
