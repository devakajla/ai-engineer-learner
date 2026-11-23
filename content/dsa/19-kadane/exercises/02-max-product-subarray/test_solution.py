import random
from solution import max_product


def brute(nums):
    best = None
    for i in range(len(nums)):
        p = 1
        for j in range(i, len(nums)):
            p *= nums[j]
            best = p if best is None else max(best, p)
    return best


def test_examples():
    assert max_product([2, 3, -2, 4]) == 6
    assert max_product([-2, 0, -1]) == 0


def test_edges():
    assert max_product([-2]) == -2
    assert max_product([-2, 3, -4]) == 24, "two negatives make a positive"
    assert max_product([0, 2]) == 2
    assert max_product([-1, -1]) == 1


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(1, 9))]
        assert max_product(nums) == brute(nums), f"{nums}"
