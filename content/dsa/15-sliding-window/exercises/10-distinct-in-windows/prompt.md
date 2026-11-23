# Distinct numbers in every window

Write `distinct_in_windows(nums, k)` that returns a list: for each window of `k` consecutive numbers (left to right), how many **different** values it holds. `1 <= k <= len(nums)`.

```python
distinct_in_windows([1, 2, 1, 3, 4, 2, 3], 4)    # -> [3, 4, 4, 3]
distinct_in_windows([5, 5, 5], 2)                # -> [1, 1]
```

**Think first:** if you only add and remove one item per step, how do you keep the distinct count up to date without calling `set()` on the whole window?

**Hint:** pattern *fixed window + counter-dict*: when a count goes `0 -> 1` the distinct number grows; when it goes `1 -> 0` it shrinks.
