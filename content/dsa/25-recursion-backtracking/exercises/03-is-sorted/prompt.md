# Is the list sorted? (recursion)

Write `is_sorted(nums)` that returns `True` if the list is in non-decreasing order, **using recursion**.

```python
is_sorted([1, 2, 2, 5])    # -> True
is_sorted([1, 3, 2])       # -> False
```

**Think first:** a list with 0 or 1 items is always sorted. For longer lists, what do you check at the front, and what do you ask the recursion?

**Hint:** pattern *check one, trust the rest*: `nums[0] <= nums[1] and is_sorted(nums[1:])`.
