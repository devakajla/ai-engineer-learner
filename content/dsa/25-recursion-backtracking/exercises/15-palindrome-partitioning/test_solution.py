import random
from itertools import combinations
from solution import partition


def brute(s):
    out = []
    n = len(s)
    for r in range(n):
        for cuts in combinations(range(1, n), r):
            b = [0, *cuts, n]
            parts = [s[x:y] for x, y in zip(b, b[1:])]
            if all(p == p[::-1] for p in parts):
                out.append(parts)
    return sorted(out)


def test_examples():
    assert sorted(partition("aab")) == [["a", "a", "b"], ["aa", "b"]]
    assert partition("a") == [["a"]]


def test_random():
    rng = random.Random(15)
    for _ in range(100):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 8)))
        assert sorted(partition(s)) == brute(s), f"{s!r}"
