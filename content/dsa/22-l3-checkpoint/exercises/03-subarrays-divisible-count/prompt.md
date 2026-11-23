# Subarrays with sum divisible by k

Write `count_divisible(nums, k)` that returns the number of **non-empty contiguous subarrays** whose sum is divisible by `k` (`k > 0`). Numbers can be negative.

```python
count_divisible([4, 5, 0, -2, -3, 1], 5)    # -> 7
count_divisible([5], 9)                     # -> 0
```

**Think first:** two prefix sums with the same remainder mod `k` give a subarray between them that is divisible by `k`.

**Hint:** pattern *prefix sum + counter-dict*: count each `prefix % k` (start with `{0: 1}`); add the count seen so far before each update. Python `%` is never negative here.
