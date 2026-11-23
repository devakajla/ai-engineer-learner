# Longest run of 1s with k flips

`nums` holds only `0` and `1`. You may flip **at most `k` zeros** into ones. Write `longest_ones(nums, k)` that returns the longest run of ones you can get.

```python
longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)    # -> 6
longest_ones([0, 0, 0], 0)                            # -> 0
```

**Think first:** you do not need to really flip anything. What must be true about the zeros inside a good window?

**Hint:** pattern *variable window, maximum*: count zeros in the window; `while zeros > k:` shrink.
