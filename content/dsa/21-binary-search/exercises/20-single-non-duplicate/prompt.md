# Single element in a sorted list

`nums` is sorted. Every value appears **exactly twice**, except one value that appears **once**. Write `single_non_duplicate(nums)` that returns that value. It must run in O(log n) and O(1) space.

```python
single_non_duplicate([1, 1, 2, 3, 3, 4, 4, 8, 8])    # -> 2
single_non_duplicate([3, 3, 7, 7, 10, 11, 11])       # -> 10
```

**Think first:** before the single value, pairs start at **even** indexes (`0, 2, 4, ...`). After the single value, they start at odd indexes. How can you use that at `mid`?

**Hint:** pattern *binary search on parity*: make `mid` even (`mid -= mid % 2`); if `nums[mid] == nums[mid + 1]` the single is to the right (`lo = mid + 2`), else `hi = mid`.
