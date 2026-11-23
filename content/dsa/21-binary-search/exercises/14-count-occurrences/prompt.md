# Count occurrences in a sorted list

`nums` is sorted ascending and may have duplicates. Write `count_occurrences(nums, target)` that returns how many times `target` appears. It must be O(log n), so do not loop over the whole list.

```python
count_occurrences([1, 2, 2, 2, 3, 5], 2)    # -> 3
count_occurrences([1, 2, 3], 4)             # -> 0
```

**Think first:** if you know the index where the `target`s **start** and the index where they **end**, the count is a subtraction.

**Hint:** pattern *lower bound twice*: `first_ge(target)` is the first index with `nums[i] >= target`; the count is `first_ge(target + 1) - first_ge(target)` (integers).
