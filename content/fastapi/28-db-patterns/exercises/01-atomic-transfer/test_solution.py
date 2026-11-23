import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from solution import Account, Base, InsufficientFunds, open_account, transfer


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def balances(engine_session, *ids):
    engine_session.expire_all()
    return [engine_session.get(Account, i).balance for i in ids]


def test_open_account(session):
    a = open_account(session, "ann", 50)
    assert a.id and a.balance == 50
    assert open_account(session, "bob").balance == 0


def test_transfer_moves_money(session):
    a, b = open_account(session, "a", 100), open_account(session, "b")
    assert transfer(session, a.id, b.id, 30) is None
    assert balances(session, a.id, b.id) == [70, 30]


def test_transfer_everything(session):
    a, b = open_account(session, "a", 100), open_account(session, "b", 5)
    transfer(session, a.id, b.id, 100)
    assert balances(session, a.id, b.id) == [0, 105]


def test_insufficient_funds_changes_nothing(session):
    a, b = open_account(session, "a", 100), open_account(session, "b")
    with pytest.raises(InsufficientFunds):
        transfer(session, a.id, b.id, 101)
    assert balances(session, a.id, b.id) == [100, 0]


@pytest.mark.parametrize("amount", [0, -5])
def test_bad_amount(session, amount):
    a, b = open_account(session, "a", 100), open_account(session, "b")
    with pytest.raises(ValueError):
        transfer(session, a.id, b.id, amount)
    assert balances(session, a.id, b.id) == [100, 0]


def test_same_account(session):
    a = open_account(session, "a", 100)
    with pytest.raises(ValueError):
        transfer(session, a.id, a.id, 10)
    assert balances(session, a.id) == [100]


def test_missing_accounts_change_nothing(session):
    a = open_account(session, "a", 100)
    with pytest.raises(LookupError):
        transfer(session, a.id, 999, 10)
    with pytest.raises(LookupError):
        transfer(session, 999, a.id, 10)
    assert balances(session, a.id) == [100]


def test_session_usable_after_failure(session):
    a, b = open_account(session, "a", 10), open_account(session, "b")
    with pytest.raises(InsufficientFunds):
        transfer(session, a.id, b.id, 50)
    transfer(session, a.id, b.id, 10)
    assert balances(session, a.id, b.id) == [0, 10]


def test_total_money_is_constant(session):
    accounts = [open_account(session, f"u{i}", 100) for i in range(3)]
    for src, dst, amt in [(0, 1, 40), (1, 2, 500), (2, 0, 100), (0, 2, 10)]:
        try:
            transfer(session, accounts[src].id, accounts[dst].id, amt)
        except InsufficientFunds:
            pass
    assert sum(balances(session, *[a.id for a in accounts])) == 300
