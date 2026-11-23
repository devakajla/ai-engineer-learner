import random
from solution import all_paths


def brute(graph):
    n = len(graph)
    out = []
    frontier = [[0]]
    while frontier:
        nxt = []
        for p in frontier:
            if p[-1] == n - 1:
                out.append(p)
            else:
                for nb in graph[p[-1]]:
                    nxt.append(p + [nb])
        frontier = nxt
    return sorted(out)


def test_examples():
    assert all_paths([[1, 2], [3], [3], []]) == [[0, 1, 3], [0, 2, 3]]
    assert all_paths([[]]) == [[0]]


def test_random():
    rng = random.Random(16)
    for _ in range(200):
        n = rng.randint(1, 7)
        graph = [[b for b in range(a + 1, n) if rng.random() < 0.4] for a in range(n)]
        assert all_paths([list(g) for g in graph]) == brute(graph), f"{graph}"
