import random
from solution import find_min


def test_examples():
    assert find_min([3, 4, 5, 1, 2]) == 1
    assert find_min([4, 5, 6, 7, 0, 1, 2]) == 0


def test_edges():
    assert find_min([1]) == 1
    assert find_min([2, 1]) == 1
    assert find_min([1, 2, 3]) == 1, "not rotated"
    assert find_min([2, 3, 1]) == 1


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        base = sorted(rng.sample(range(-30, 30), rng.randint(1, 12)))
        k = rng.randint(0, len(base) - 1)
        nums = base[k:] + base[:k]
        assert find_min(nums) == base[0], f"{nums}"
