import random
from solution import remove_duplicates


def check(nums):
    want = sorted(set(nums))
    work = list(nums)
    k = remove_duplicates(work)
    assert k == len(want), f"{nums}: expected k={len(want)}, got {k}"
    assert work[:k] == want, f"{nums}: first k items should be {want}, got {work[:k]}"


def test_examples():
    nums = [1, 1, 2, 2, 3]
    assert remove_duplicates(nums) == 3
    assert nums[:3] == [1, 2, 3]
    assert remove_duplicates([]) == 0


def test_edges():
    check([7])
    check([4, 4, 4, 4])
    check([1, 2, 3])
    check([-2, -2, 0, 0, 5])


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        check(sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 12))))
