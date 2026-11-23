from solution import vowel_count


def test_examples():
    assert vowel_count("Python") == 1
    assert vowel_count("AEIOU xyz") == 5


def test_more():
    assert vowel_count("") == 0
    assert vowel_count("rhythm") == 0
    assert vowel_count("Education") == 5
