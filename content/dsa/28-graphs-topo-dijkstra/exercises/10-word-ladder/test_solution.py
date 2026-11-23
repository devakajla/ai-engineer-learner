import random
from solution import ladder_length


def brute(begin, end, words):
    nodes = [begin] + [w for w in dict.fromkeys(words) if w != begin]
    if end not in nodes:
        return 0
    n = len(nodes)
    INF = 10 ** 9
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if sum(a != b for a, b in zip(nodes[i], nodes[j])) == 1:
                d[i][j] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    steps = d[0][nodes.index(end)]
    return 0 if steps >= INF else steps + 1


def test_examples():
    assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


def test_edges():
    assert ladder_length("a", "c", ["a", "b", "c"]) == 2


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        words = list({"".join(rng.choice("abc") for _ in range(3)) for _ in range(rng.randint(1, 8))})
        begin = "".join(rng.choice("abc") for _ in range(3))
        end = rng.choice(words)
        assert ladder_length(begin, end, list(words)) == brute(begin, end, words), f"{begin}, {end}, {words}"
