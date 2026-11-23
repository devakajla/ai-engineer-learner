# Min and max together

Write `min_max(nums)` that returns `(smallest, largest)` for a non-empty list. Use a loop, not `min` / `max`.

```python
min_max([4, 1, 9])    # -> (1, 9)
min_max([5])          # -> (5, 5)
```

**Think first:** you need two "best so far" variables.

**Hint:** start both from `nums[0]`.
