# Longest turbulent subarray

A part is **turbulent** if the comparison sign between neighbours **flips** every step (up, down, up, ... or down, up, down, ...). Write `longest_turbulent(arr)` that returns the length of the longest turbulent contiguous part. A single element counts as length 1.

```python
longest_turbulent([9, 4, 2, 10, 7, 8, 8, 1, 9])    # -> 5   ([4, 2, 10, 7, 8])
longest_turbulent([4, 8, 12, 16])                  # -> 2
```

**Think first:** this is Kadane on "the current streak": extend it when the sign flips, restart when it does not. What do equal neighbours do?

**Hint:** pattern *Kadane streak*: compare `arr[i] > arr[i-1]` with the previous sign; extend `cur += 1` if it flipped, else `cur = 2` (or `1` if equal).
