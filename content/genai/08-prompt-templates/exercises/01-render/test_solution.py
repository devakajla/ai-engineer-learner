import pytest

from solution import render


def test_examples():
    assert render("Hi {name}!", {"name": "Dev"}) == "Hi Dev!"
    assert render("Hi {name}!", {"name": "Dev", "x": 1}) == "Hi Dev!"
    assert render("No holes", {}) == "No holes"


def test_missing_variable():
    with pytest.raises(ValueError) as info:
        render("Hi {name}!", {})
    assert str(info.value) == "missing variable: name"


def test_which_name_is_reported():
    with pytest.raises(ValueError, match="missing variable: city"):
        render("{name} lives in {city}", {"name": "Dev"})


def test_doubled_braces():
    assert render('JSON: {{"a": "{x}"}}', {"x": "1"}) == 'JSON: {"a": "1"}'
