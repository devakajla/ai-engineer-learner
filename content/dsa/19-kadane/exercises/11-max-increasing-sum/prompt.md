# Maximum ascending subarray sum

Write `max_increasing_sum(nums)` that returns the largest sum of a contiguous part where **every number is bigger than the one before** (a part of length 1 counts). Return `0` for an empty list.

```python
max_increasing_sum([10, 20, 30, 5, 10, 50])           # -> 65   (5 + 10 + 50)
max_increasing_sum([12, 17, 15, 13, 10, 11, 12])      # -> 33   (10 + 11 + 12)
```

**Think first:** when the increasing streak breaks, what happens to the running sum?

**Hint:** pattern *Kadane streak*: if `x > previous`, `cur += x`, else `cur = x`. Track the best.
