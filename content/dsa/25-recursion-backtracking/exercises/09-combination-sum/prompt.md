# Combination sum

`candidates` has **different positive** numbers. Write `combination_sum(candidates, target)` that returns all **unique** combinations that add up to `target`. You may use the same number **many times**. Return each combination as a list in the order of `candidates`; the order of the combinations does not matter.

```python
combination_sum([2, 3, 6, 7], 7)    # -> [[2, 2, 3], [7]]   (any order)
combination_sum([2], 1)             # -> []
```

**Think first:** for each candidate, do you take it (and may take it again) or move to the next one? When do you stop?

**Hint:** pattern *take (stay) / skip (move on)*: `go(i, remaining)`: if `remaining == 0` save; if `remaining < 0` or `i == len(candidates)` stop; take `candidates[i]` and call `go(i, remaining - c)`; undo; then `go(i + 1, remaining)`.
