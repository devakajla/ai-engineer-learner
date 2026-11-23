import random
from solution import group_anagrams


def brute(words):
    groups = []
    for w in words:
        for g in groups:
            if sorted(g[0]) == sorted(w):
                g.append(w)
                break
        else:
            groups.append([w])
    return groups


def test_examples():
    assert group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    assert group_anagrams([""]) == [[""]]


def test_edges():
    assert group_anagrams([]) == []
    assert group_anagrams(["a"]) == [["a"]]
    assert group_anagrams(["ab", "ba", "ab"]) == [["ab", "ba", "ab"]]


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(0, 3))) for _ in range(rng.randint(0, 8))]
        assert group_anagrams(words) == brute(words), f"{words}"
