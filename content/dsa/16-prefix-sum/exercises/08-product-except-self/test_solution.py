import random
from solution import product_except_self


def brute(nums):
    out = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        out.append(p)
    return out


def test_examples():
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_except_self([2, 0, 3]) == [0, 6, 0]


def test_edges():
    assert product_except_self([]) == []
    assert product_except_self([7]) == [1]
    assert product_except_self([0, 0, 2]) == [0, 0, 0]


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        nums = [rng.randint(-3, 4) for _ in range(rng.randint(0, 8))]
        assert product_except_self(nums) == brute(nums), f"{nums}"
