import sqlite3


def setup(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0))"
    )
    conn.executemany("INSERT INTO accounts (id, owner, balance) VALUES (?, ?, ?)", [(1, "dev", 100), (2, "ana", 50)])
    conn.commit()


def transfer(conn, from_id, to_id, amount):
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
    conn.commit()
