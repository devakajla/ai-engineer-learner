# Insert an interval

`intervals` is a list of **non-overlapping** intervals `[start, end]` **sorted by start**. Write `insert_interval(intervals, new)` that adds `new` and merges whatever overlaps or touches. Return the sorted list. O(n), no re-sorting.

```python
insert_interval([[1, 3], [6, 9]], [2, 5])                     # -> [[1, 5], [6, 9]]
insert_interval([[1, 2], [3, 5], [6, 7], [8, 10]], [4, 8])    # -> [[1, 2], [3, 10]]
```

**Think first:** the list splits into 3 parts: intervals fully **before** `new`, intervals that **overlap** it, intervals fully **after**. How do you test each?

**Hint:** pattern *three phases*: copy while `end < new_start`; merge while `start <= new_end` (take min start, max end); copy the rest.
