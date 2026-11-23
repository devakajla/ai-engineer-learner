import random
from itertools import permutations
from solution import alien_order


def sorted_by(words, order):
    rank = {ch: i for i, ch in enumerate(order)}
    keys = [[rank[ch] for ch in w] for w in words]
    return all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1))


def brute(words):
    letters = sorted({ch for w in words for ch in w})
    for perm in permutations(letters):
        if sorted_by(words, perm):
            return "".join(perm)
    return ""


def test_examples():
    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
    assert alien_order(["z", "x", "z"]) == ""


def test_edges():
    assert alien_order([]) == ""
    assert alien_order(["ab", "a"]) == ""
    assert alien_order(["abc"]) == "abc"


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        order = rng.sample("abcd", rng.randint(2, 4))
        rank = {ch: i for i, ch in enumerate(order)}
        words = ["".join(rng.choice(order) for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(1, 5))]
        words.sort(key=lambda w: [rank[ch] for ch in w])
        assert alien_order(list(words)) == brute(words), f"{words}"
