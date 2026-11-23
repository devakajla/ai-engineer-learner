import random
from solution import can_finish


def brute(n, prereqs):
    reach = [[False] * n for _ in range(n)]
    for a, b in prereqs:
        reach[b][a] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return not any(reach[i][i] for i in range(n))


def test_examples():
    assert can_finish(2, [[1, 0]]) is True
    assert can_finish(2, [[1, 0], [0, 1]]) is False


def test_edges():
    assert can_finish(0, []) is True
    assert can_finish(3, []) is True
    assert can_finish(1, [[0, 0]]) is False


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        n = rng.randint(1, 6)
        prereqs = [[a, b] for a in range(n) for b in range(n) if a != b and rng.random() < 0.15]
        assert can_finish(n, prereqs) is brute(n, prereqs), f"{n}, {prereqs}"
