# Count triplets that sum to zero

Write `count_zero_triplets(nums)` that returns how many **different value triplets** `(a, b, c)` with `a <= b <= c` and `a + b + c == 0` can be made from different positions of `nums`. Two triplets are the same if they have the same values.

```python
count_zero_triplets([-1, 0, 1, 2, -1, -4])    # -> 2    ([-1, -1, 2] and [-1, 0, 1])
count_zero_triplets([0, 0, 0, 0])             # -> 1
```

**Think first:** if you fix the first number, what is left? Is it a problem you already know?

**Hint:** pattern *sort + two pointers*: sort, fix `i`, then move `lo`/`hi` inward; skip equal values to avoid duplicate triplets.
