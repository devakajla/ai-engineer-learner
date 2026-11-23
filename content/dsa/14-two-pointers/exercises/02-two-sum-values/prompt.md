# Two Sum on an unsorted list (values)

`nums` is **not** sorted. Write `two_sum_values(nums, target)` that returns the pair of **values** `[a, b]` with `a <= b` that add up to `target`, using two different positions. If several pairs exist return the one with the **smallest `a`**. Return `[]` if none. Do not use a set or dict: sort, then use two pointers.

```python
two_sum_values([7, 2, 11, 4], 9)     # -> [2, 7]
two_sum_values([3, 3], 6)            # -> [3, 3]
```

**Think first:** why can you sort here, but not if the question asked for the original **indexes**?

**Hint:** `nums = sorted(nums)` (a copy), then the same two-end loop as the previous exercise.
