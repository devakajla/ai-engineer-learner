# Smallest divisor given a threshold

Write `smallest_divisor(nums, threshold)` that returns the **smallest positive integer** `d` such that the sum of `ceil(n / d)` over all numbers in `nums` is `<= threshold`. (`threshold >= len(nums)`, all numbers are positive.)

```python
smallest_divisor([1, 2, 5, 9], 6)      # -> 5
smallest_divisor([44, 22, 33, 11, 1], 5)   # -> 44
```

**Think first:** a bigger divisor makes the sum smaller or equal. So the answer sits on a boundary between "too small" and "enough".

**Hint:** pattern *binary search on the answer*: `lo = 1`, `hi = max(nums)`; `total = sum((n + d - 1) // d for n in nums)`; if `total <= threshold` try smaller.
