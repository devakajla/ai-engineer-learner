from solution import count_vowels


def test_examples():
    assert count_vowels("Python") == 1
    assert count_vowels("AEIOU xyz") == 5
    assert count_vowels("") == 0


def test_more():
    assert count_vowels("rhythm") == 0
    assert count_vowels("banana") == 3
    assert count_vowels("Education") == 5
