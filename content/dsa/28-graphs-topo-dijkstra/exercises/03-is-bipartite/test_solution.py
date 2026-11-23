import random
from itertools import product
from solution import is_bipartite


def brute(graph):
    n = len(graph)
    for colours in product((0, 1), repeat=n):
        if all(colours[a] != colours[b] for a in range(n) for b in graph[a]):
            return True
    return False


def test_examples():
    assert is_bipartite([[1, 3], [0, 2], [1, 3], [0, 2]]) is True
    assert is_bipartite([[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]) is False


def test_edges():
    assert is_bipartite([]) is True
    assert is_bipartite([[]]) is True
    assert is_bipartite([[1, 2], [0, 2], [0, 1]]) is False, "triangle"


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        n = rng.randint(1, 7)
        graph = [[] for _ in range(n)]
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < 0.3:
                    graph[a].append(b)
                    graph[b].append(a)
        assert is_bipartite([list(g) for g in graph]) is brute(graph), f"{graph}"
