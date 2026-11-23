import random
from solution import max_overlap


def brute(iv):
    if not iv:
        return 0
    return max(sum(1 for s, e in iv if s <= p <= e) for p in range(0, 25))


def test_examples():
    assert max_overlap([[1, 4], [2, 5], [7, 9]]) == 2
    assert max_overlap([[1, 3], [3, 5]]) == 2


def test_edges():
    assert max_overlap([]) == 0
    assert max_overlap([[2, 2]]) == 1
    assert max_overlap([[1, 2], [3, 4]]) == 1, "3 is after 2: no shared point"


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        iv = []
        for _ in range(rng.randint(0, 7)):
            s = rng.randint(0, 12)
            iv.append([s, s + rng.randint(0, 6)])
        assert max_overlap(iv) == brute(iv), f"{iv}"
