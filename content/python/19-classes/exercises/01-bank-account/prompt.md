# Bank account

Write a class `BankAccount`:

- `BankAccount(owner, balance=0)` — `balance` must not be negative (raise `ValueError`)
- `deposit(amount)` — amount must be > 0 (else `ValueError`); returns the new balance
- `withdraw(amount)` — amount must be > 0; if it's more than the balance raise `ValueError("insufficient funds")`; returns the new balance
- `balance` is a **read-only property** (assigning `acc.balance = 5` must raise `AttributeError`)
- `__repr__` returns `BankAccount(owner='Dev', balance=100)`

```python
acc = BankAccount("Dev", 100)
acc.deposit(50)      # -> 150
acc.withdraw(30)     # -> 120
acc.balance          # -> 120
repr(acc)            # -> "BankAccount(owner='Dev', balance=120)"
```
