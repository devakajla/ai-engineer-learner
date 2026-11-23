# Move money: all or nothing

With SQLAlchemy 2.0 (no FastAPI), write:

- `class Base(DeclarativeBase)`
- `class InsufficientFunds(Exception)`
- model `Account` → table `accounts`: `id` (PK), `owner` (`String(50)`, required), `balance` (int, default `0`)
- `open_account(session, owner, balance=0) -> Account` (commit + refresh, return it)
- `transfer(session, from_id, to_id, amount) -> None`

Rules for `transfer`:

- `amount` must be above 0, and the two ids must be different. Otherwise raise `ValueError`.
- If either account does not exist, raise `LookupError`.
- If the source has less than `amount`, raise `InsufficientFunds`.
- On success, **both** balances change and are committed together.
- On **any** failure, **nothing** changes. Call `session.rollback()` and raise the error again.

```text
a=100, b=0   transfer(a, b, 30)   -> a=70,  b=30
a=100, b=0   transfer(a, b, 500)  -> InsufficientFunds, a=100, b=0
```

**Think first:** If the money leaves account `a` and then the program fails before it reaches `b`, what would be lost? What makes the two changes one unit?

**Hint:** One transaction = one `commit()` at the end, `rollback()` in `except`. For the balance check without a race, use `update(Account).where(Account.id == from_id, Account.balance >= amount).values(balance=Account.balance - amount)` and look at `result.rowcount`.
