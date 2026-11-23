# Rotate right

Write `rotate_right(nums, k)` that returns a new list rotated to the right by `k` places. `k` can be larger than the length.

```python
rotate_right([1, 2, 3, 4, 5], 2)   # -> [4, 5, 1, 2, 3]
rotate_right([1, 2, 3], 4)         # -> [3, 1, 2]
rotate_right([], 3)                # -> []
```

**Think first:** rotating by the length gives the same list. So what is the real `k`?

**Hint:** `k % len(nums)` and slicing `nums[-k:] + nums[:-k]`. Watch `k == 0`.
