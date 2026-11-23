import random
from solution import mst_cost


def kruskal(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for w, u, v in sorted((w, u, v) for u, v, w in edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total


def test_examples():
    assert mst_cost(4, [[0, 1, 1], [1, 2, 2], [0, 2, 3], [2, 3, 1]]) == 4
    assert mst_cost(1, []) == 0


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [[i, rng.randrange(i), rng.randint(1, 9)] for i in range(1, n)]
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < 0.3:
                    edges.append([a, b, rng.randint(1, 9)])
        assert mst_cost(n, [list(e) for e in edges]) == kruskal(n, edges), f"{n}, {edges}"
