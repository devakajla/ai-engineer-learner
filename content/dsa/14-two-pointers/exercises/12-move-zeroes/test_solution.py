import random
from solution import move_zeroes


def check(nums):
    want = [x for x in nums if x != 0] + [0] * nums.count(0)
    work = list(nums)
    res = move_zeroes(work)
    assert res is None, "change the list in place and return None"
    assert work == want, f"{nums}: expected {want}, got {work}"


def test_examples():
    check([0, 1, 0, 3, 12])
    check([0])


def test_edges():
    check([])
    check([5])
    check([0, 0, 0])
    check([1, 2, 3])
    check([0, 0, 1])
    check([-1, 0, -2, 0, 0, 7])


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        check([rng.choice([0, 0, 1, 2, -3]) for _ in range(rng.randint(0, 12))])
