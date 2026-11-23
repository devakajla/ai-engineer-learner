import random
from solution import min_cost_connect


def kruskal(points):
    n = len(points)
    edges = sorted((abs(points[a][0] - points[b][0]) + abs(points[a][1] - points[b][1]), a, b)
                   for a in range(n) for b in range(a + 1, n))
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    total = 0
    for w, a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += w
    return total


def test_examples():
    assert min_cost_connect([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
    assert min_cost_connect([[0, 0]]) == 0


def test_edges():
    assert min_cost_connect([[1, 1], [1, 1]]) == 0
    assert min_cost_connect([[0, 0], [3, 4]]) == 7


def test_random():
    rng = random.Random(12)
    for _ in range(200):
        pts = [[rng.randint(-6, 6), rng.randint(-6, 6)] for _ in range(rng.randint(1, 8))]
        assert min_cost_connect([list(p) for p in pts]) == kruskal(pts), f"{pts}"
