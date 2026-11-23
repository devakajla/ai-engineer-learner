import random
from solution import count_components


def brute(n, edges):
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            m = min(label[a], label[b])
            if label[a] != m or label[b] != m:
                label[a] = label[b] = m
                changed = True
    return len(set(label))


def test_examples():
    assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
    assert count_components(3, []) == 3


def test_edges():
    assert count_components(0, []) == 0
    assert count_components(1, []) == 1


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        n = rng.randint(0, 8)
        edges = [[a, b] for a in range(n) for b in range(a + 1, n) if rng.random() < 0.2]
        assert count_components(n, edges) == brute(n, edges), f"{n}, {edges}"
