# Maximum subarray sum with length at least k

Write `max_sum_at_least_k(nums, k)` that returns the largest sum of a contiguous part with **at least `k` elements**. `1 <= k <= len(nums)`. O(n).

```python
max_sum_at_least_k([-1, -2, 3, 4, -5], 2)    # -> 7    ([3, 4])
max_sum_at_least_k([-5, -3], 2)              # -> -8
```

**Think first:** a part ending at `i` with length at least `k` starts at `i - k + 1` or earlier. Which earlier start is best?

**Hint:** pattern *prefix sum + running minimum*: `prefix[i + 1] - min(prefix[0..i + 1 - k])`. Keep that minimum as you go.
