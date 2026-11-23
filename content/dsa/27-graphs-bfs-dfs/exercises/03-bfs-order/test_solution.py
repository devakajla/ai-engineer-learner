import random
from solution import bfs_order


def reference(graph, start):
    order, seen, frontier = [start], {start}, [start]
    while frontier:
        nxt = []
        for node in frontier:
            for nb in graph[node]:
                if nb not in seen:
                    seen.add(nb)
                    order.append(nb)
                    nxt.append(nb)
        frontier = nxt
    return order


def test_examples():
    g = {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}
    assert bfs_order(g, 0) == [0, 1, 2, 3]


def test_edges():
    assert bfs_order({0: []}, 0) == [0]


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        n = rng.randint(1, 8)
        g = {i: [] for i in range(n)}
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < 0.3:
                    g[a].append(b)
                    g[b].append(a)
        for v in g:
            rng.shuffle(g[v])
        assert bfs_order(g, 0) == reference(g, 0), f"{g}"
