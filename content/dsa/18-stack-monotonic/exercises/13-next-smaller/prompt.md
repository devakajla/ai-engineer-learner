# Next smaller element

Write `next_smaller(nums)` that returns, for each item, the **first strictly smaller value to its right**, or `-1` if none.

```python
next_smaller([4, 8, 5, 2, 25])    # -> [2, 5, 2, -1, -1]
next_smaller([1, 2, 3])           # -> [-1, -1, -1]
```

**Think first:** it is the mirror of "next greater". Which comparison flips, and what order does the stack keep now?

**Hint:** pattern *monotonic stack (increasing)*: `while stack and nums[stack[-1]] > x:` pop and answer with `x`.
