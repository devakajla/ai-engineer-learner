# Maximum circular subarray sum

The list is **circular**: the part may wrap around from the end to the start (but each element is used at most once). Write `max_circular(nums)` that returns the largest sum of a non-empty part.

```python
max_circular([5, -3, 5])        # -> 10   (5 + 5, wrapping)
max_circular([-3, -2, -3])      # -> -2
```

**Think first:** a wrapping part is "everything" minus a middle part. Which middle part should you remove to make the rest as big as possible?

**Hint:** pattern *Kadane twice*: answer is `max(max_subarray, total - min_subarray)`. If all numbers are negative, `total - min_subarray` would be empty, so return `max_subarray`.
