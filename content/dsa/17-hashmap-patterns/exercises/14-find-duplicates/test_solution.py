import random
from solution import find_duplicates


def test_examples():
    assert find_duplicates([4, 3, 2, 7, 8, 2, 3, 1]) == [2, 3]
    assert find_duplicates([1, 2, 3]) == []


def test_edges():
    assert find_duplicates([]) == []
    assert find_duplicates([5, 5, 5, 5]) == [5], "each value once"
    assert find_duplicates([-1, -1, 0, 0, 0]) == [-1, 0]


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
        assert find_duplicates(nums) == sorted(x for x in set(nums) if nums.count(x) >= 2), f"{nums}"
