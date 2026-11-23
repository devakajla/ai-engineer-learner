import random
from solution import max_probability


def brute(n, edges, probs, s, t):
    best = [0.0]

    def go(node, p, seen):
        if node == t:
            best[0] = max(best[0], p)
            return
        for (a, b), q in zip(edges, probs):
            for u, v in ((a, b), (b, a)):
                if u == node and v not in seen:
                    go(v, p * q, seen | {v})

    go(s, 1.0, {s})
    return best[0]


def test_examples():
    assert abs(max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2) - 0.25) < 1e-9
    assert max_probability(3, [[0, 1]], [0.5], 0, 2) == 0.0


def test_edges():
    assert max_probability(1, [], [], 0, 0) == 1.0


def test_random():
    rng = random.Random(15)
    for _ in range(200):
        n = rng.randint(1, 6)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.4]
        probs = [rng.choice([0.1, 0.25, 0.5, 0.8, 1.0]) for _ in edges]
        s, t = rng.randrange(n), rng.randrange(n)
        got = max_probability(n, [list(e) for e in edges], list(probs), s, t)
        assert abs(got - brute(n, edges, probs, s, t)) < 1e-9, f"{n}, {edges}, {probs}, {s}, {t}"
