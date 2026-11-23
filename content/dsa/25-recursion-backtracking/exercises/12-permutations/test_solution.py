import random
from itertools import permutations as perms
from solution import permutations


def test_examples():
    assert sorted(permutations([1, 2, 3])) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    assert permutations([]) == [[]]


def test_random():
    rng = random.Random(12)
    for _ in range(60):
        v = rng.sample(range(-9, 10), rng.randint(0, 6))
        got = permutations(list(v))
        assert sorted(got) == sorted(list(p) for p in perms(v)), f"{v}"
