# Smallest subarray with sum at least target

`nums` has **positive** integers. Write `min_len_subarray(nums, target)` that returns the length of the shortest contiguous part whose sum is `>= target`. Return `0` if no part works. Aim for O(n).

```python
min_len_subarray([2, 3, 1, 2, 4, 3], 7)    # -> 2   ([4, 3])
min_len_subarray([1, 1, 1], 10)            # -> 0
```

**Think first:** once the window is big enough, can you throw away its left side and still be big enough? Keep doing that.

**Hint:** pattern *variable window, minimum*: add `nums[hi]`, then `while total >= target:` record the length and shrink from the left.
