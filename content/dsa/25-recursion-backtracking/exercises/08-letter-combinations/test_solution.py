import random
from itertools import product
from solution import letter_combinations

L = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def test_examples():
    assert letter_combinations("23") == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
    assert letter_combinations("") == []


def test_edges():
    assert letter_combinations("7") == ["p", "q", "r", "s"]


def test_random():
    rng = random.Random(8)
    for _ in range(100):
        d = "".join(rng.choice("23456789") for _ in range(rng.randint(1, 4)))
        want = ["".join(p) for p in product(*(L[c] for c in d))]
        assert letter_combinations(d) == want, f"{d!r}"
