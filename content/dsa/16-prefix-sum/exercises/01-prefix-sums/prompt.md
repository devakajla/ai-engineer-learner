# Build the prefix sums

Write `prefix_sums(nums)` that returns a list where item `i` is `nums[0] + ... + nums[i]` (a running sum).

```python
prefix_sums([1, 2, 3, 4])    # -> [1, 3, 6, 10]
prefix_sums([])              # -> []
```

**Think first:** how is `prefix[i]` related to `prefix[i - 1]`?

**Hint:** pattern *prefix array*: keep a running `total` and append it every step.
