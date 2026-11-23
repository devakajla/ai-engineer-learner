import random
from solution import sort_colors


def check(nums):
    work = list(nums)
    res = sort_colors(work)
    assert res is None, "change the list in place and return None"
    assert work == sorted(nums), f"{nums}: expected {sorted(nums)}, got {work}"


def test_examples():
    check([2, 0, 2, 1, 1, 0])
    check([2, 0, 1])


def test_edges():
    check([])
    check([1])
    check([2, 2, 2])
    check([2, 1, 0])
    check([0, 1, 2, 0, 1, 2])
    check([1, 2, 0, 0, 2, 1, 1])


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        check([rng.randint(0, 2) for _ in range(rng.randint(0, 12))])
