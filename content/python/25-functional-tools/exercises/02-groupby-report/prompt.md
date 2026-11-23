# Group orders into a report

Each order: `{"user": "dev", "status": "paid", "amount": 250.0}`.

Write `status_report(orders)` returning a list of `(status, count, total_amount)` tuples, **one per status**, sorted by status name, with `total_amount` rounded to 2 decimals. Use `itertools.groupby` (remember what it needs first!).

```python
status_report([
    {"user": "a", "status": "paid", "amount": 10.0},
    {"user": "b", "status": "cancelled", "amount": 5.0},
    {"user": "c", "status": "paid", "amount": 2.5},
])
# -> [("cancelled", 1, 5.0), ("paid", 2, 12.5)]
```

Also write `top_spenders(orders, n)` → list of the `n` user names with the highest total of **non-cancelled** orders, highest first (ties: name ascending).
