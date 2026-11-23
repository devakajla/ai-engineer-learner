import random
from solution import find_order


def has_cycle(n, prereqs):
    reach = [[False] * n for _ in range(n)]
    for a, b in prereqs:
        reach[b][a] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return any(reach[i][i] for i in range(n))


def test_examples():
    assert find_order(2, [[1, 0]]) == [0, 1]
    assert find_order(2, [[1, 0], [0, 1]]) == []


def test_edges():
    assert find_order(0, []) == []
    assert sorted(find_order(3, [])) == [0, 1, 2]


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(1, 6)
        prereqs = [[a, b] for a in range(n) for b in range(n) if a != b and rng.random() < 0.2]
        got = find_order(n, prereqs)
        if has_cycle(n, prereqs):
            assert got == [], f"{n}, {prereqs}: a cycle means no order"
        else:
            assert sorted(got) == list(range(n)), f"{n}, {prereqs}: every course once"
            pos = {c: i for i, c in enumerate(got)}
            for a, b in prereqs:
                assert pos[b] < pos[a], f"{b} must come before {a}"
