import random
from solution import covered_length


def brute(iv):
    return len({x for s, e in iv for x in range(s, e)})


def test_examples():
    assert covered_length([[1, 3], [2, 5]]) == 4
    assert covered_length([[1, 2], [2, 3]]) == 2


def test_edges():
    assert covered_length([]) == 0
    assert covered_length([[0, 10], [2, 3]]) == 10
    assert covered_length([[1, 2], [5, 6]]) == 2
    assert covered_length([[4, 4]]) == 0


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        iv = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 12)
            iv.append([s, s + rng.randint(0, 5)])
        assert covered_length(iv) == brute(iv), f"{iv}"
