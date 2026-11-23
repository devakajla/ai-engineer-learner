import random
from collections import Counter
from solution import top_k_words


def test_examples():
    assert top_k_words(["i", "love", "code", "i", "love", "dsa"], 2) == ["i", "love"]
    assert top_k_words(["b", "a", "b", "a", "c"], 3) == ["a", "b", "c"]


def test_edges():
    assert top_k_words(["x"], 1) == ["x"]


def test_random():
    rng = random.Random(17)
    for _ in range(200):
        words = [rng.choice(["a", "b", "c", "d", "e"]) for _ in range(rng.randint(1, 14))]
        c = Counter(words)
        k = rng.randint(1, len(c))
        want = [w for w, _ in sorted(c.items(), key=lambda p: (-p[1], p[0]))][:k]
        assert top_k_words(words, k) == want, f"{words}, {k}"
