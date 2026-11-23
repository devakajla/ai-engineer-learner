import random
from solution import reverse_vowels


def expected(s):
    vs = [c for c in s if c in "aeiouAEIOU"][::-1]
    it = iter(vs)
    return "".join(next(it) if c in "aeiouAEIOU" else c for c in s)


def test_examples():
    assert reverse_vowels("hello") == "holle"
    assert reverse_vowels("leetcode") == "leotcede"


def test_edges():
    assert reverse_vowels("") == ""
    assert reverse_vowels("xyz") == "xyz", "no vowels"
    assert reverse_vowels("a") == "a"
    assert reverse_vowels("aA") == "Aa", "case is kept with the letter"
    assert reverse_vowels("Aeiou") == "uoieA"


def test_random():
    rng = random.Random(14)
    for _ in range(300):
        s = "".join(rng.choice("aeiouAEIOUxyz ") for _ in range(rng.randint(0, 12)))
        assert reverse_vowels(s) == expected(s), f"{s!r}"
