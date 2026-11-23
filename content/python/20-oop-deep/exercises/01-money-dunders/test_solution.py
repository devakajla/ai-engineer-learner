import pytest

from solution import Money


def test_repr_eq_add():
    assert repr(Money(500)) == "Money(500, 'INR')"
    assert Money(500) + Money(250) == Money(750)
    assert Money(1) != Money(1, "USD")
    assert (Money(1) == 1) is False


def test_hash():
    assert len({Money(1), Money(1), Money(2)}) == 2
    assert {Money(5): "x"}[Money(5)] == "x"


def test_ordering():
    assert sorted([Money(3), Money(1), Money(2)]) == [Money(1), Money(2), Money(3)]
    assert min([Money(9), Money(4)]) == Money(4)
    with pytest.raises(ValueError):
        Money(1) < Money(1, "USD")


def test_add_currency_mismatch():
    with pytest.raises(ValueError):
        Money(1) + Money(1, "USD")


def test_bool():
    assert not Money(0) and Money(1)
