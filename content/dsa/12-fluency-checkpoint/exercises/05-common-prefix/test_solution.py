from solution import common_prefix


def test_examples():
    assert common_prefix(["flower", "flow", "flight"]) == "fl"
    assert common_prefix(["dog", "car"]) == ""
    assert common_prefix(["same"]) == "same"


def test_more():
    assert common_prefix([]) == ""
    assert common_prefix(["ab", "ab"]) == "ab"
    assert common_prefix(["abc", "ab"]) == "ab", "one word is shorter"
    assert common_prefix(["", "a"]) == ""
