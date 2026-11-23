import random
from solution import single_non_duplicate


def test_examples():
    assert single_non_duplicate([1, 1, 2, 3, 3, 4, 4, 8, 8]) == 2
    assert single_non_duplicate([3, 3, 7, 7, 10, 11, 11]) == 10


def test_edges():
    assert single_non_duplicate([5]) == 5
    assert single_non_duplicate([1, 2, 2]) == 1
    assert single_non_duplicate([1, 1, 2]) == 2


def test_random():
    rng = random.Random(20)
    for _ in range(400):
        vals = sorted(rng.sample(range(-20, 40), rng.randint(1, 10)))
        single = rng.choice(vals)
        nums = sorted([v for v in vals for _ in range(2)] )
        nums.remove(single)
        assert single_non_duplicate(nums) == single, f"{nums}"
