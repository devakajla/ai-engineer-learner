# Daily temperatures

`temps[i]` is the temperature of day `i`. Write `daily_temperatures(temps)` that returns, for each day, **how many days you must wait** for a warmer temperature. Use `0` if there is no warmer day.

```python
daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])    # -> [1, 1, 4, 2, 1, 1, 0, 0]
daily_temperatures([30, 20, 10])                        # -> [0, 0, 0]
```

**Think first:** this is "next greater" again, but the answer is a **distance**, not a value. What must you store in the stack to compute it?

**Hint:** pattern *monotonic stack of indexes*: when popping index `j` because of day `i`, the answer for `j` is `i - j`.
