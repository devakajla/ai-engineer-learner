# Many range updates

Start with a list of `n` zeros. Each update is `[left, right, value]`: add `value` to **every** item from `left` to `right` (both included). Write `apply_updates(n, updates)` that returns the final list. It must be fast when there are many updates.

```python
apply_updates(5, [[1, 3, 2], [2, 4, 3], [0, 2, -2]])    # -> [-2, 0, 3, 5, 3]
apply_updates(3, [])                                    # -> [0, 0, 0]
```

**Think first:** instead of touching every item in the range, can you mark only where the change **starts** and where it **stops**?

**Hint:** pattern *difference array*: `diff[left] += value`, `diff[right + 1] -= value` (make `diff` one longer), then the answer is the running sum of `diff`.
