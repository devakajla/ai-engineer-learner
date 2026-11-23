import pytest

from solution import BankAccount


def test_flow():
    acc = BankAccount("Dev", 100)
    assert acc.deposit(50) == 150
    assert acc.withdraw(30) == 120
    assert acc.balance == 120
    assert repr(acc) == "BankAccount(owner='Dev', balance=120)"


def test_default_balance():
    assert BankAccount("A").balance == 0


def test_errors():
    with pytest.raises(ValueError):
        BankAccount("A", -1)
    acc = BankAccount("A", 10)
    with pytest.raises(ValueError):
        acc.deposit(0)
    with pytest.raises(ValueError):
        acc.withdraw(-5)
    with pytest.raises(ValueError, match="insufficient funds"):
        acc.withdraw(11)
    assert acc.balance == 10, "failed operations must not change the balance"


def test_balance_read_only():
    acc = BankAccount("A", 10)
    with pytest.raises(AttributeError):
        acc.balance = 1_000_000
