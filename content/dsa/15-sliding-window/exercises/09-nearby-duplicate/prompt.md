# Contains nearby duplicate

Write `contains_nearby_duplicate(nums, k)` that returns `True` if there are two **different indexes** `i < j` with `nums[i] == nums[j]` and `j - i <= k`. Otherwise `False`.

```python
contains_nearby_duplicate([1, 2, 3, 1], 3)          # -> True
contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)    # -> False
```

**Think first:** at index `j` which earlier items are allowed to match? How many of them are there?

**Hint:** pattern *fixed window + seen-set*: keep a set of the last `k` items; before moving on, remove the item that falls out of the window.
