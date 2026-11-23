import random
from solution import count_below


def test_examples():
    assert count_below([1, 3, 3, 5, 8], 4) == 3
    assert count_below([1, 3, 3, 5, 8], 1) == 0


def test_edges():
    assert count_below([], 5) == 0
    assert count_below([2, 2, 2], 2) == 0
    assert count_below([2, 2, 2], 3) == 3


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        nums = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 12)))
        x = rng.randint(-7, 7)
        assert count_below(nums, x) == sum(1 for n in nums if n < x), f"{nums}, {x}"
