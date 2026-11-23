# Count the ways, without repeating work

A child climbs a staircase of `n` steps. Each move can go up 1, 2 or 3 steps. Different **orders** count as different ways: for `n = 3` the ways are `1+1+1`, `1+2`, `2+1` and `3`, so there are 4.

Write `count_ways(n)`:

- `count_ways(0)` is `1` (the child is already at the top: one way, do nothing).
- `count_ways(n)` for `n < 0` raises `ValueError`.
- It must be fast: the tests call `count_ways(60)`, which takes years if you recalculate the same sub-problem again and again.

```python
count_ways(3)     # -> 4
count_ways(4)     # -> 7
count_ways(60)    # -> 4680045560037375
```

**Think first:** To reach step `n`, from which steps could the last move have come? How often is `count_ways(10)` worked out in a plain recursive solution?

**Hint:** `count_ways(n) = count_ways(n-1) + count_ways(n-2) + count_ways(n-3)`, with a cache (`functools.cache`) or a loop that keeps the last three values.
