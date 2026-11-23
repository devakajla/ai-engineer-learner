# Longest subarray with sum k

`nums` can have **negative** numbers. Write `longest_sum_k(nums, k)` that returns the length of the longest contiguous subarray whose sum is exactly `k`. Return `0` if none.

```python
longest_sum_k([1, -1, 5, -2, 3], 3)    # -> 4   ([1, -1, 5, -2])
longest_sum_k([-2, -1, 2, 1], 1)       # -> 2
```

**Think first:** for the **longest** one you want the **earliest** place where each prefix value appeared. What do you store in the dict?

**Hint:** pattern *prefix sum + first-index dict*: `first = {0: -1}`; only save a prefix value the first time you see it.
