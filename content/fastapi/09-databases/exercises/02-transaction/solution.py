import sqlite3


def setup(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0))"
    )
    conn.executemany("INSERT INTO accounts (id, owner, balance) VALUES (?, ?, ?)", [(1, "dev", 100), (2, "ana", 50)])
    conn.commit()


def transfer(conn: sqlite3.Connection, from_id: int, to_id: int, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")
    with conn:  # one transaction: commit on success, rollback on any exception
        debit = conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
        if debit.rowcount != 1:
            raise LookupError(f"account {from_id} not found")
        credit = conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
        if credit.rowcount != 1:
            raise LookupError(f"account {to_id} not found")
