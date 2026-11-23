import random
from solution import partition_labels


def brute(s):
    cuts = [0] + [i for i in range(1, len(s)) if not (set(s[:i]) & set(s[i:]))] + [len(s)]
    return [b - a for a, b in zip(cuts, cuts[1:])] if s else []


def test_examples():
    assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
    assert partition_labels("eccbbbbdec") == [10]


def test_edges():
    assert partition_labels("") == []
    assert partition_labels("a") == [1]
    assert partition_labels("abc") == [1, 1, 1]
    assert partition_labels("aaa") == [3]


def test_random():
    rng = random.Random(14)
    for _ in range(400):
        s = "".join(rng.choice("abcde") for _ in range(rng.randint(0, 10)))
        assert partition_labels(s) == brute(s), f"{s!r}"
