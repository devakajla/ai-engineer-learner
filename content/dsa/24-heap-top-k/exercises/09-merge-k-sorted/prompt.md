# Merge K sorted lists

`lists` is a list of sorted Python lists (some may be empty). Write `merge_k_sorted(lists)` that returns one sorted list with all the numbers. Use a heap of size `len(lists)`; do not concatenate and sort.

```python
merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])    # -> [1, 1, 2, 3, 4, 4, 5, 6]
merge_k_sorted([[], []])                          # -> []
```

**Think first:** at any time, the next output is the smallest of the **current front** items. How many fronts do you need to remember?

**Hint:** pattern *k-way merge*: push `(lists[i][0], i, 0)`; pop `(v, i, j)`, append `v`, and push `(lists[i][j + 1], i, j + 1)` if it exists.
