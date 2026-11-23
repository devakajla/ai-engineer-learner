# Binary subarrays with sum

`nums` holds only `0` and `1`. Write `binary_subarrays_sum(nums, goal)` that counts the contiguous subarrays with sum exactly `goal` (`goal >= 0`).

```python
binary_subarrays_sum([1, 0, 1, 0, 1], 2)    # -> 4
binary_subarrays_sum([0, 0, 0, 0, 0], 0)    # -> 15
```

**Think first:** it is the same question as "subarray sum equals k". Which tool did you use there?

**Hint:** pattern *prefix sum + counter-dict*.
