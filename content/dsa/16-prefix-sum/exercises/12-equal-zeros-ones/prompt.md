# Equal number of 0s and 1s

`nums` holds only `0` and `1`. Write `equal_zeros_ones(nums)` that returns the length of the longest contiguous subarray with **the same number of 0s and 1s**. Return `0` if none.

```python
equal_zeros_ones([0, 1])          # -> 2
equal_zeros_ones([0, 1, 0])       # -> 2
```

**Think first:** if every `0` counted as `-1`, what would "equal numbers" mean for the sum?

**Hint:** pattern *prefix sum + first-index dict*: turn `0` into `-1`, then it is "longest subarray with sum 0" (exercise 10 with `k = 0`).
