# Atomic money transfer

`setup(conn)` (given) creates `accounts(id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0))` with two rows.

Write `transfer(conn, from_id, to_id, amount)`:

- `amount` must be > 0, else `ValueError`
- both UPDATEs happen in **one transaction**: if anything fails (unknown account, the CHECK constraint fires because of insufficient funds, ...) **nothing** changes
- unknown account → raise `LookupError` (check `cursor.rowcount`)
- insufficient funds → the database's CHECK raises `sqlite3.IntegrityError`; let it propagate after rolling back

Hint: `with conn:` commits on success and rolls back on exception.

```python
transfer(conn, 1, 2, 30)   # balances: 1 -> 70, 2 -> 80
transfer(conn, 1, 2, 500)  # IntegrityError, balances unchanged
```
