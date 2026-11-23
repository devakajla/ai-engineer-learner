from solution import truncate_result


def test_short_text_is_unchanged():
    assert truncate_result("hello", 10) == "hello"
    assert truncate_result("hello", 5) == "hello", "exactly at the limit is fine"
    assert truncate_result("", 3) == ""


def test_long_text_is_cut_with_a_note():
    assert truncate_result("abcdefghij", 4) == "abcd\n[truncated 6 more characters]"
    assert truncate_result("abcdef", 5) == "abcde\n[truncated 1 more characters]"


def test_zero_limit():
    assert truncate_result("abc", 0) == "\n[truncated 3 more characters]"


def test_the_note_counts_characters_not_words():
    text = "word " * 100
    out = truncate_result(text, 50)
    assert out.startswith(text[:50]) and out.endswith("[truncated 450 more characters]")
