# Maximum subarray sum

Write `max_subarray(nums)` that returns the largest sum of a **non-empty contiguous** part of `nums`. The numbers can be negative. O(n), one pass.

```python
max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])    # -> 6    ([4, -1, 2, 1])
max_subarray([-3, -1, -2])                       # -> -1
```

**Think first:** standing at index `i`, the best part that **ends here** either starts fresh at `i`, or extends the best part that ended at `i - 1`. When is extending a bad idea?

**Hint:** pattern *Kadane*: `ending_here = max(x, ending_here + x)`; `best = max(best, ending_here)`. Start both with `nums[0]`.
