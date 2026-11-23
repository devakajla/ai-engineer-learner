import random
from solution import four_sum_count


def brute(a, b, c, d):
    return sum(1 for w in a for x in b for y in c for z in d if w + x + y + z == 0)


def test_examples():
    assert four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2]) == 2
    assert four_sum_count([0], [0], [0], [0]) == 1


def test_edges():
    assert four_sum_count([], [], [], []) == 0
    assert four_sum_count([1], [1], [1], [1]) == 0
    assert four_sum_count([0, 0], [0, 0], [0, 0], [0, 0]) == 16


def test_random():
    rng = random.Random(13)
    for _ in range(150):
        n = rng.randint(0, 4)
        lists = [[rng.randint(-2, 2) for _ in range(n)] for _ in range(4)]
        assert four_sum_count(*lists) == brute(*lists), f"{lists}"
