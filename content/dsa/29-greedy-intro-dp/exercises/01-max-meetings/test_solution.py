import random
from itertools import combinations
from solution import max_meetings


def brute(meetings):
    best = 0
    n = len(meetings)
    for mask in range(1 << n):
        chosen = sorted(meetings[i] for i in range(n) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best


def test_examples():
    assert max_meetings([[1, 3], [2, 4], [3, 5]]) == 2
    assert max_meetings([]) == 0


def test_random():
    rng = random.Random(1)
    for _ in range(200):
        ms = []
        for _ in range(rng.randint(0, 8)):
            a = rng.randint(0, 8)
            ms.append([a, a + rng.randint(1, 4)])
        assert max_meetings([list(m) for m in ms]) == brute(ms), f"{ms}"
