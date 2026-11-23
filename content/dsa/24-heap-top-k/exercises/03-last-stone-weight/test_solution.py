import random
from solution import last_stone_weight


def brute(stones):
    s = sorted(stones)
    while len(s) > 1:
        a, b = s.pop(), s.pop()
        if a != b:
            s.append(a - b)
            s.sort()
    return s[0] if s else 0


def test_examples():
    assert last_stone_weight([2, 7, 4, 1, 8, 1]) == 1
    assert last_stone_weight([5]) == 5


def test_edges():
    assert last_stone_weight([]) == 0
    assert last_stone_weight([3, 3]) == 0


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        v = [rng.randint(1, 20) for _ in range(rng.randint(0, 9))]
        assert last_stone_weight(list(v)) == brute(v), f"{v}"
