# Find a peak element

In `nums` **neighbours are always different**. A **peak** is an item bigger than both neighbours (outside the list counts as minus infinity, so an end item only needs to beat its one neighbour). Write `find_peak(nums)` that returns the index of **any** peak. O(log n). The list is **not sorted**.

```python
find_peak([1, 2, 3, 1])          # -> 2
find_peak([1, 2, 1, 3, 5, 6, 4]) # -> 1 or 5
```

**Think first:** you stand at `mid` and it is going up to the right (`nums[mid] < nums[mid + 1]`). Is there surely a peak on the right?

**Hint:** pattern *binary search on a slope*: `if nums[mid] < nums[mid + 1]: lo = mid + 1 else: hi = mid`; loop `while lo < hi`.
