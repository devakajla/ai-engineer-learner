import pytest

from solution import parse_age


def test_valid():
    assert parse_age("25") == 25
    assert parse_age("0") == 0
    assert parse_age("150") == 150


def test_not_a_number():
    with pytest.raises(ValueError, match="age must be a number"):
        parse_age("abc")
    with pytest.raises(ValueError, match="age must be a number"):
        parse_age("")


def test_out_of_range():
    with pytest.raises(ValueError, match="age out of range"):
        parse_age("-1")
    with pytest.raises(ValueError, match="age out of range"):
        parse_age("151")
