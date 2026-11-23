# Combination sum II (each number once)

`candidates` may contain duplicates. Write `combination_sum2(candidates, target)` that returns all **unique** combinations (sorted lists) that add up to `target`. Each item of `candidates` can be used **at most once**. Any order of results.

```python
combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)    # -> [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]   (any order)
combination_sum2([2, 5, 2, 1, 2], 5)           # -> [[1, 2, 2], [5]]                        (any order)
```

**Think first:** this mixes two earlier ideas: "choose from a start index" and "skip equal siblings". Where does each one go?

**Hint:** pattern *sorted + skip equal siblings*: sort; `go(start, remaining)`: for `i` in `start..`: skip if `i > start and c[i] == c[i - 1]`; stop if `c[i] > remaining`; append, `go(i + 1, remaining - c[i])`, pop.
