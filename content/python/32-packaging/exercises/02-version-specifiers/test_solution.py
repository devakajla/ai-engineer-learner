import pytest

from solution import parse_version, satisfies


def test_parse_version():
    assert parse_version("1.10.0") == (1, 10, 0)
    assert parse_version("2") == (2,)
    assert parse_version(" 3.1 ") == (3, 1)


@pytest.mark.parametrize("bad", ["1.x.0", "", "a", "1..2"])
def test_parse_version_bad(bad):
    with pytest.raises(ValueError):
        parse_version(bad)


def test_numbers_not_text():
    assert satisfies("1.10.0", ">1.9.0"), "1.10.0 is newer than 1.9.0"
    assert not satisfies("1.9.0", ">1.10.0")


def test_range():
    assert satisfies("1.10.0", ">=1.9,<2.0")
    assert not satisfies("2.0.0", ">=1.9,<2.0")
    assert not satisfies("1.8.9", ">=1.9,<2.0")
    assert satisfies("1.9", ">=1.9,<2.0")


def test_equal_and_not_equal():
    assert satisfies("1.4", "==1.4.0"), "a shorter version counts as if it ended with zeros"
    assert satisfies("1.4.0", "==1.4")
    assert not satisfies("1.4.1", "==1.4")
    assert satisfies("1.4.1", "!=1.4")
    assert not satisfies("1.4", "!=1.4.0")


def test_less_equal():
    assert satisfies("1.0.0", "<=1.0")
    assert not satisfies("1.0.1", "<=1.0")


def test_empty_rule_accepts_all():
    assert satisfies("0.0.1", "")
    assert satisfies("99.0", "  ")


def test_spaces_ignored():
    assert satisfies("1.5.0", " >= 1.4 , < 2.0 ".replace(" ", ""))
    assert satisfies("1.5.0", ">=1.4, <2.0")


def test_unknown_operator():
    with pytest.raises(ValueError):
        satisfies("1.0", "~~1.0")
    with pytest.raises(ValueError):
        satisfies("1.0", "1.0")
