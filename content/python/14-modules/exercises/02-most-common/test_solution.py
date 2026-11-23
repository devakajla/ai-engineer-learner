from solution import most_common_letter


def test_examples():
    assert most_common_letter("Hello World") == "l"
    assert most_common_letter("abab") == "a"
    assert most_common_letter("123 !") is None


def test_more():
    assert most_common_letter("") is None
    assert most_common_letter("Zzz a") == "z"
    assert most_common_letter("ba") == "a", "tie goes to the earlier letter"
