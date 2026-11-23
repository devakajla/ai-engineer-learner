# Search in a rotated sorted list

`nums` is a sorted list of **unique** values that was **rotated**. Write `search_rotated(nums, target)` that returns the index of `target`, or `-1`. O(log n).

```python
search_rotated([4, 5, 6, 7, 0, 1, 2], 0)    # -> 4
search_rotated([4, 5, 6, 7, 0, 1, 2], 3)    # -> -1
```

**Think first:** at any `mid`, **one** of the two halves is fully sorted. How do you find which one, and how do you check if `target` is inside it?

**Hint:** pattern *binary search with a sorted half*: if `nums[lo] <= nums[mid]` the left half is sorted: if `nums[lo] <= target < nums[mid]` go left, else right. Otherwise the right half is sorted.
