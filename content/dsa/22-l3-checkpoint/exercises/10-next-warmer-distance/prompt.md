# Pick the pattern: days until a warmer day

Write `days_until_warmer(temps)` that returns, for each day, how many days you must wait for a **warmer** day (`0` if never).

```python
days_until_warmer([73, 74, 75, 71, 69, 72, 76, 73])    # -> [1, 1, 4, 2, 1, 1, 0, 0]
days_until_warmer([30, 20, 10])                        # -> [0, 0, 0]
```

**Think first:** which earlier days are still "waiting" when a new day arrives? In what order should they be answered?

**Hint:** pattern *monotonic stack of indices*: while `temps[i] > temps[stack[-1]]`, pop and set `answer[j] = i - j`.
