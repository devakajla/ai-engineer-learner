from solution import count_pairs


def test_example():
    assert count_pairs("the cat sat the cat ran") == {
        "the": {"cat": 2},
        "cat": {"sat": 1, "ran": 1},
        "sat": {"the": 1},
    }


def test_short_text():
    assert count_pairs("Hi") == {}, "one word has no pair"
    assert count_pairs("") == {}, "empty text gives an empty dictionary"


def test_lowercase_and_spaces():
    assert count_pairs("A  b A B") == {"a": {"b": 2}, "b": {"a": 1}}, (
        "lowercase the text and let split() handle extra spaces"
    )


def test_last_word_has_no_row():
    result = count_pairs("a b c")
    assert "c" not in result, "the last word has nothing after it"
    assert result == {"a": {"b": 1}, "b": {"c": 1}}
