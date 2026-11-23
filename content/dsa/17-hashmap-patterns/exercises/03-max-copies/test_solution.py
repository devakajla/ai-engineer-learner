import random
from solution import max_copies


def brute(text, word):
    k = 0
    pool = list(text)
    while True:
        for ch in word:
            if ch in pool:
                pool.remove(ch)
            else:
                return k
        k += 1


def test_examples():
    assert max_copies("loonbalxballpoon", "balloon") == 2
    assert max_copies("leetcode", "balloon") == 0


def test_edges():
    assert max_copies("nlaebolko", "balloon") == 1
    assert max_copies("", "ab") == 0
    assert max_copies("aaaa", "aa") == 2


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        text = "".join(rng.choice("abc") for _ in range(rng.randint(0, 14)))
        word = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
        assert max_copies(text, word) == brute(text, word), f"{text!r}, {word!r}"
