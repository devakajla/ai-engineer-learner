# Merge two sorted lists (two pointers)

Both lists are sorted. Write `merge_sorted(a, b)` that returns a new sorted list in O(n + m). Do **not** call `sort`/`sorted`. Do not change `a` or `b`.

```python
merge_sorted([1, 3, 5], [2, 4, 6])    # -> [1, 2, 3, 4, 5, 6]
merge_sorted([1, 2], [])              # -> [1, 2]
```

**Think first:** when the loop ends, one list may still have items. Are they already in order?

**Hint:** pattern *two lists*: `i` and `j`, append the smaller front item, move that pointer. After the loop, append the leftovers.
