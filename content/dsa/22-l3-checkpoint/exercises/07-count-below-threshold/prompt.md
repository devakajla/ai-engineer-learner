# Count items below a value in a sorted list

`nums` is sorted ascending. Write `count_below(nums, x)` that returns how many items are **strictly less than** `x`, in O(log n).

```python
count_below([1, 3, 3, 5, 8], 4)    # -> 3
count_below([1, 3, 3, 5, 8], 1)    # -> 0
```

**Think first:** the answer is the index of the first item that is `>= x`.

**Hint:** pattern *lower bound / first True*: `lo, hi = 0, len(nums)`; `nums[mid] < x` means `lo = mid + 1`, else `hi = mid`.
