# Classic binary search

`nums` is sorted ascending with **unique** values. Write `binary_search(nums, target)` that returns the index of `target`, or `-1`. It must take O(log n) steps.

```python
binary_search([-1, 0, 3, 5, 9, 12], 9)    # -> 4
binary_search([-1, 0, 3, 5, 9, 12], 2)    # -> -1
```

**Think first:** after you look at the middle item, which half can you throw away for sure?

**Hint:** pattern *halve the range*: `lo, hi = 0, len(nums) - 1`; `while lo <= hi:` `mid = (lo + hi) // 2`; move `lo = mid + 1` or `hi = mid - 1`.
