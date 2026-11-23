import random
from solution import remove_element


def check(nums, val):
    want = [x for x in nums if x != val]
    work = list(nums)
    k = remove_element(work, val)
    assert k == len(want), f"{nums}, {val}: expected k={len(want)}, got {k}"
    assert work[:k] == want, f"{nums}, {val}: first k items should be {want}, got {work[:k]}"


def test_examples():
    check([3, 2, 2, 3], 3)
    check([1, 2], 9)


def test_edges():
    check([], 1)
    check([4], 4)
    check([4, 4, 4], 4)
    check([0, 1, 0, 2, 0], 0)


def test_random():
    rng = random.Random(11)
    for _ in range(200):
        check([rng.randint(0, 3) for _ in range(rng.randint(0, 10))], rng.randint(0, 3))
