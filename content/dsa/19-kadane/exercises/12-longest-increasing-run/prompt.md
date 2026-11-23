# Longest increasing run

Write `longest_increasing_run(nums)` that returns the length of the longest **contiguous** part that is **strictly increasing**. Return `0` for an empty list.

```python
longest_increasing_run([1, 3, 5, 4, 7])    # -> 3
longest_increasing_run([2, 2, 2])          # -> 1
```

**Think first:** this is not the famous "longest increasing subsequence": here the items must be next to each other. What decides if the run continues?

**Hint:** pattern *Kadane streak*: `run = run + 1 if nums[i] > nums[i - 1] else 1`.
