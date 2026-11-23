import sqlite3

import pytest

from solution import setup, transfer


def balances(conn):
    return dict(conn.execute("SELECT id, balance FROM accounts").fetchall())


def make():
    conn = sqlite3.connect(":memory:")
    setup(conn)
    return conn


def test_ok():
    conn = make()
    transfer(conn, 1, 2, 30)
    assert balances(conn) == {1: 70, 2: 80}


def test_insufficient_funds_rolls_back():
    conn = make()
    with pytest.raises(sqlite3.IntegrityError):
        transfer(conn, 1, 2, 500)
    assert balances(conn) == {1: 100, 2: 50}


def test_unknown_account_rolls_back():
    conn = make()
    with pytest.raises(LookupError):
        transfer(conn, 1, 99, 10)
    assert balances(conn) == {1: 100, 2: 50}, "the debit must be rolled back too"


def test_bad_amount():
    conn = make()
    with pytest.raises(ValueError):
        transfer(conn, 1, 2, 0)
