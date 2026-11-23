# Two Sum (unsorted)

Write `two_sum(nums, target)` that returns `[i, j]` with `i < j` and `nums[i] + nums[j] == target`. The list is **not sorted** and you must not change the order. Return `[]` if there is no pair. If several pairs exist, any one is fine. O(n).

```python
two_sum([2, 7, 11, 15], 9)    # -> [0, 1]
two_sum([3, 3], 6)            # -> [0, 1]
```

**Think first:** standing at `x`, which value would finish the pair? Have you already seen it?

**Hint:** pattern *seen-dict*: `index_of[value] = i`; for each `x` check `target - x` in the dict **before** storing `x`.
