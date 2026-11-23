# Two Sum in a sorted list

`nums` is sorted in ascending order. Write `two_sum_sorted(nums, target)` that returns `[i, j]` (0-based, `i < j`) with `nums[i] + nums[j] == target`. Return `[]` if no pair exists. If several pairs exist, any one is fine. Use two pointers: O(n), no extra space.

```python
two_sum_sorted([1, 2, 4, 7, 11], 9)    # -> [1, 3]
two_sum_sorted([1, 2, 3], 10)          # -> []
```

**Think first:** if `nums[left] + nums[right]` is too big, which pointer can safely move?

**Hint:** pattern *opposite ends*: `left, right = 0, len(nums) - 1`, `while left < right`.
