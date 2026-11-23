import random
from solution import merge_sorted


def test_examples():
    assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    assert merge_sorted([1, 2], []) == [1, 2]


def test_edges():
    assert merge_sorted([], []) == []
    assert merge_sorted([], [3]) == [3]
    assert merge_sorted([1, 1], [1]) == [1, 1, 1]
    assert merge_sorted([5, 6], [1, 2]) == [1, 2, 5, 6], "all of b is smaller"
    assert merge_sorted([-3, 0], [-5, 4, 9]) == [-5, -3, 0, 4, 9]


def test_inputs_unchanged_and_random():
    a, b = [1, 4], [2, 3]
    merge_sorted(a, b)
    assert a == [1, 4] and b == [2, 3], "do not modify the input lists"
    rng = random.Random(4)
    for _ in range(200):
        x = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 8)))
        y = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 8)))
        assert merge_sorted(x, y) == sorted(x + y), f"{x} + {y}"
