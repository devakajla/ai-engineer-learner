import random
from solution import dfs_order


def reference(graph, start):
    order, stack, seen = [], [start], set()
    # iterative preorder DFS: push neighbours in reverse so the first listed is visited first
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nb in reversed(graph[node]):
            if nb not in seen:
                stack.append(nb)
    return order


def test_examples():
    g = {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}
    assert dfs_order(g, 0) == [0, 1, 3, 2]


def test_edges():
    assert dfs_order({0: []}, 0) == [0]
    assert dfs_order({0: [1], 1: [0], 2: []}, 0) == [0, 1], "node 2 is not reachable"


def test_random():
    rng = random.Random(2)
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
        assert dfs_order(g, 0) == reference(g, 0), f"{g}"
