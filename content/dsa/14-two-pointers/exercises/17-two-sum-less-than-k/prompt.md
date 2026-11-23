# Two Sum less than K

Write `two_sum_less_than_k(nums, k)` that returns the **largest** sum `nums[i] + nums[j]` (different positions) that is **strictly less than `k`**. Return `-1` if no pair works. `nums` is not sorted and has only positive numbers.

```python
two_sum_less_than_k([34, 23, 1, 24, 75, 33, 54, 8], 60)    # -> 58    (34 + 24)
two_sum_less_than_k([10, 20, 30], 15)                      # -> -1
```

**Think first:** when `s < k`, you record it, and then which pointer moves to try for a bigger sum?

**Hint:** sort a copy, two-end loop: if `s < k` update `best` and `left += 1`, else `right -= 1`.
