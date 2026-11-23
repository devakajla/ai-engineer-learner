from solution import group_anagrams


def test_examples():
    result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert result == [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]


def test_more():
    assert group_anagrams([]) == []
    assert group_anagrams(["a"]) == [["a"]]
    assert group_anagrams(["ab", "ba", "ab"]) == [["ab", "ba", "ab"]]
