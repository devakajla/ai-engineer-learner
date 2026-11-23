import random
from solution import binary_search


def test_examples():
    assert binary_search([-1, 0, 3, 5, 9, 12], 9) == 4
    assert binary_search([-1, 0, 3, 5, 9, 12], 2) == -1


def test_edges():
    assert binary_search([], 1) == -1
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1
    assert binary_search([1, 2], 1) == 0
    assert binary_search([1, 2], 2) == 1


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        nums = sorted(rng.sample(range(-20, 20), rng.randint(0, 12)))
        t = rng.randint(-22, 22)
        want = nums.index(t) if t in nums else -1
        assert binary_search(nums, t) == want, f"{nums}, {t}"
