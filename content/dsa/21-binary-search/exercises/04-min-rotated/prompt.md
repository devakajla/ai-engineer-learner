# Minimum in a rotated sorted list

A sorted list with **unique** values was **rotated** (some items from the front moved to the back): `[0, 1, 2, 4, 5, 6, 7]` can become `[4, 5, 6, 7, 0, 1, 2]`. Write `find_min(nums)` that returns the smallest value. O(log n).

```python
find_min([3, 4, 5, 1, 2])         # -> 1
find_min([4, 5, 6, 7, 0, 1, 2])   # -> 0
```

**Think first:** compare `nums[mid]` with the **last** item. If `nums[mid]` is bigger, on which side is the "drop"?

**Hint:** pattern *binary search on a shape*: `if nums[mid] > nums[hi]: lo = mid + 1 else: hi = mid`; loop `while lo < hi`.
