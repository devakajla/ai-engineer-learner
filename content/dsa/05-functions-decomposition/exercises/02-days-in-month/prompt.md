# Days in a month

Write `days_in_month(month, year)` using your own leap-year logic. `month` is 1-12.

```python
days_in_month(1, 2023)   # -> 31
days_in_month(2, 2024)   # -> 29
days_in_month(2, 2023)   # -> 28
days_in_month(4, 2023)   # -> 30
```

**Think first:** which month is special? Can you reuse a helper?

**Hint:** write `is_leap` again inside this file as a helper, and keep a list of month lengths.
