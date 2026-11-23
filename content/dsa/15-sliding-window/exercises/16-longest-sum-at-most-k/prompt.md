# Longest subarray with sum at most k

`nums` has **non-negative** integers (zeros allowed). Write `longest_sum_at_most(nums, k)` that returns the length of the longest contiguous part whose sum is `<= k`. Return `0` if even a single item is too big.

```python
longest_sum_at_most([1, 2, 1, 0, 1, 1, 0], 4)    # -> 5   ([1, 0, 1, 1, 0])
longest_sum_at_most([5, 6], 4)                   # -> 0
```

**Think first:** this is the mirror of exercise 02. There we shrank while the window was big **enough**. Here we shrink while it is **too big**.

**Hint:** pattern *variable window, maximum*: add `nums[hi]`; `while total > k:` shrink from the left; then update the best length.
