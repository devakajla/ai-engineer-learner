# Leap year

Write `is_leap(year)`. A year is a leap year if it is divisible by 4, except years divisible by 100 are not, unless also divisible by 400.

```python
is_leap(2024)   # -> True
is_leap(1900)   # -> False
is_leap(2000)   # -> True
```

**Think first:** list the three rules as a small table with example years.

**Hint:** `and` / `or` with `%`.
