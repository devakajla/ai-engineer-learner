import random
from solution import count_shortest_paths


def brute(n, edges):
    paths = []

    def go(node, cost, seen):
        if node == n - 1:
            paths.append(cost)
            return
        for u, v, w in edges:
            for a, b in ((u, v), (v, u)):
                if a == node and b not in seen:
                    go(b, cost + w, seen | {b})

    go(0, 0, {0})
    if not paths:
        return 0
    return paths.count(min(paths))


def test_examples():
    assert count_shortest_paths(4, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]]) == 2
    assert count_shortest_paths(3, [[0, 1, 1]]) == 0


def test_edges():
    assert count_shortest_paths(1, []) == 1


def test_random():
    rng = random.Random(16)
    for _ in range(200):
        n = rng.randint(1, 6)
        edges = [[a, b, rng.randint(1, 3)] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.45]
        assert count_shortest_paths(n, [list(e) for e in edges]) == brute(n, edges), f"{n}, {edges}"
