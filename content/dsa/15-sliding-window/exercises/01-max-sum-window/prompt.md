# Maximum sum of k in a row

Write `max_sum_window(nums, k)` that returns the biggest sum of any `k` **consecutive** items. `1 <= k <= len(nums)`. Do it in O(n): do not re-add `k` numbers for every window.

```python
max_sum_window([2, 1, 5, 1, 3, 2], 3)    # -> 9   (5 + 1 + 3)
max_sum_window([4], 1)                   # -> 4
```

**Think first:** when the window moves one step right, which one number enters and which one leaves?

**Hint:** pattern *fixed window*: build the first window sum, then `total += nums[i] - nums[i - k]`.
