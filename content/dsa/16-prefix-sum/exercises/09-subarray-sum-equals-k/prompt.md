# Subarray sum equals k

`nums` can have **negative** numbers. Write `subarray_sum_k(nums, k)` that counts the contiguous subarrays whose sum is exactly `k`.

```python
subarray_sum_k([1, 1, 1], 2)    # -> 2
subarray_sum_k([1, 2, 3], 3)    # -> 2    ([1, 2] and [3])
```

**Think first:** a subarray sum is `prefix[j] - prefix[i]`. If you stand at `j`, which earlier prefix value do you need? How many times did you see it?

**Hint:** pattern *prefix sum + counter-dict*: `seen = {0: 1}`; at each step `count += seen.get(total - k, 0)`, then record `total`. (Sliding window fails here because of negatives.)
