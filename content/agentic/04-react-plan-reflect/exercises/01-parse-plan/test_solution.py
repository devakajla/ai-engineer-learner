from solution import parse_plan


def test_both_number_styles():
    assert parse_plan("1. Find the file\n2) Read it") == ["Find the file", "Read it"]


def test_other_lines_are_skipped():
    text = "Here is the plan:\n\n1. First\nSome note\n2. Second\nGood luck!"
    assert parse_plan(text) == ["First", "Second"]


def test_no_steps():
    assert parse_plan("") == []
    assert parse_plan("no steps here") == []


def test_indented_lines_and_big_numbers():
    assert parse_plan("   1.  Spaced out  \n  10) Ten") == ["Spaced out", "Ten"]


def test_empty_step_text_is_skipped():
    assert parse_plan("1.\n2. Real") == ["Real"]


def test_numbers_are_ignored():
    assert parse_plan("3. c\n1. a") == ["c", "a"]


def test_digits_without_a_dot_are_not_steps():
    assert parse_plan("2024 was a good year\n1 apple") == []
