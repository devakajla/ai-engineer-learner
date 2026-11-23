# Search insert position

`nums` is sorted ascending with unique values. Write `search_insert(nums, target)` that returns the index of `target` if it is there, otherwise the index where it **would be inserted** to keep the list sorted. O(log n).

```python
search_insert([1, 3, 5, 6], 5)    # -> 2
search_insert([1, 3, 5, 6], 2)    # -> 1
```

**Think first:** when the loop ends without finding `target`, where do `lo` and `hi` stand?

**Hint:** pattern *lower bound*: find the first index with `nums[i] >= target`. `lo, hi = 0, len(nums)`; `while lo < hi:` if `nums[mid] < target: lo = mid + 1` else `hi = mid`.
