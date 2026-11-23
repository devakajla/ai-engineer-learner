# Maximum subarray sum with one deletion

Write `max_sum_one_deletion(nums)` that returns the largest sum of a **non-empty** contiguous part, where you may **delete at most one element** from that part (the part must still have at least one element after the deletion).

```python
max_sum_one_deletion([1, -2, 0, 3])          # -> 4    ([1, 0, 3] after deleting -2)
max_sum_one_deletion([-1, -1, -1, -1])       # -> -1
```

**Think first:** at each index, there are two states: "no deletion used yet" and "one deletion already used". What can each state become?

**Hint:** pattern *Kadane with 2 states*: `keep = max(x, keep + x)` (no deletion); `deleted = max(keep_before, deleted + x)` (delete `x` now, or already deleted). Answer is the best of both over all steps.
