from solution import decode_string


def test_examples():
    assert decode_string("3[a]2[bc]") == "aaabcbc"
    assert decode_string("3[a2[c]]") == "accaccacc"


def test_more():
    assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
    assert decode_string("abc") == "abc"
    assert decode_string("") == ""
    assert decode_string("10[a]") == "a" * 10, "multi-digit numbers"
    assert decode_string("2[a2[b]c]") == "abbcabbc"
    assert decode_string("a2[b]c") == "abbc"
