import random
from solution import find_anagrams


def brute(s, p):
    return [i for i in range(len(s) - len(p) + 1) if sorted(s[i:i + len(p)]) == sorted(p)]


def test_examples():
    assert find_anagrams("cbaebabacd", "abc") == [0, 6]
    assert find_anagrams("abab", "ab") == [0, 1, 2]


def test_edges():
    assert find_anagrams("a", "ab") == [], "p longer than s"
    assert find_anagrams("aaaa", "aa") == [0, 1, 2]
    assert find_anagrams("abc", "d") == []


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 12)))
        p = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        assert find_anagrams(s, p) == brute(s, p), f"{s!r}, {p!r}"
