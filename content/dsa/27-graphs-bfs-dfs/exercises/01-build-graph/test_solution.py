import random
from solution import build_graph


def test_examples():
    assert build_graph(3, [[0, 1], [1, 2]]) == {0: [1], 1: [0, 2], 2: [1]}
    assert build_graph(2, []) == {0: [], 1: []}


def test_random():
    rng = random.Random(1)
    for _ in range(100):
        n = rng.randint(1, 7)
        pairs = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.4]
        got = build_graph(n, [list(p) for p in pairs])
        for v in range(n):
            want = sorted([b for a, b in pairs if a == v] + [a for a, b in pairs if b == v])
            assert got[v] == want, f"node {v}"
