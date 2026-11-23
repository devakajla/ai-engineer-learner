import random
from solution import merge_k_sorted


def test_examples():
    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert merge_k_sorted([[], []]) == []


def test_edges():
    assert merge_k_sorted([]) == []
    assert merge_k_sorted([[3, 4]]) == [3, 4]


def test_random():
    rng = random.Random(9)
    for _ in range(200):
        lists = [sorted(rng.randint(-5, 9) for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 5))]
        want = sorted(x for l in lists for x in l)
        assert merge_k_sorted([list(l) for l in lists]) == want, f"{lists}"
