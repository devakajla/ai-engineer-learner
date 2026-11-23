# Subarray sums divisible by k

Write `divisible_by_k(nums, k)` that counts the contiguous subarrays whose sum is divisible by `k` (`k >= 1`). Numbers can be negative.

```python
divisible_by_k([4, 5, 0, -2, -3, 1], 5)    # -> 7
divisible_by_k([5], 9)                     # -> 0
```

**Think first:** when are two prefix sums `p[j]` and `p[i]` giving a divisible difference? Think about their remainders.

**Hint:** pattern *prefix remainder + counter-dict*: same remainder means the part between them is divisible. In Python `-3 % 5` is `2`, so the remainder is never negative. Start with `{0: 1}`.
