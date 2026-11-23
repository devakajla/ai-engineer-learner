# Running sum

Write `running_sum(nums)` that returns a new list where item `i` is the sum of `nums[0..i]`.

```python
running_sum([1, 2, 3, 4])   # -> [1, 3, 6, 10]
running_sum([])             # -> []
```

**Think first:** what do you keep between rounds?

**Hint:** `total` plus `append`.
