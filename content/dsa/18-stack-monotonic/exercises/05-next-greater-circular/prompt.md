# Next greater element in a circle

The list is **circular**: after the last item comes the first one again. Write `next_greater_circular(nums)` that returns, for each item, the first strictly bigger value you meet going right (wrapping around), or `-1`.

```python
next_greater_circular([1, 2, 1])          # -> [2, -1, 2]
next_greater_circular([1, 2, 3, 4, 3])    # -> [2, 3, 4, -1, 4]
```

**Think first:** how can you "walk twice" around the list without building a longer list?

**Hint:** pattern *monotonic stack, two rounds*: loop `i` from `0` to `2 * n - 1`, use `nums[i % n]`, but only push indexes in the first round.
