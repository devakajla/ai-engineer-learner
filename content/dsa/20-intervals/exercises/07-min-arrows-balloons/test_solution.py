import random
from solution import min_arrows


def brute(b):
    points = sorted({x for s, e in b for x in (s, e)})
    left = list(b)
    count = 0
    while left:
        best = max(points, key=lambda p: sum(1 for s, e in left if s <= p <= e))
        left = [(s, e) for s, e in left if not (s <= best <= e)]
        count += 1
    return count


def test_examples():
    assert min_arrows([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2
    assert min_arrows([[1, 2], [3, 4], [5, 6], [7, 8]]) == 4


def test_edges():
    assert min_arrows([]) == 0
    assert min_arrows([[1, 2], [2, 3], [3, 4], [4, 5]]) == 2, "touching balloons share a point"
    assert min_arrows([[5, 5]]) == 1


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        b = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 10)
            b.append([s, s + rng.randint(0, 4)])
        assert min_arrows(b) == brute(b), f"{b}"
