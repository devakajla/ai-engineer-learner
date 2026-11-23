# Best sightseeing pair

`values[i]` is the score of spot `i`. A pair `i < j` has score `values[i] + values[j] + i - j` (far spots lose points). Write `best_sightseeing(values)` that returns the biggest pair score. The list has at least 2 items.

```python
best_sightseeing([8, 1, 5, 2, 6])    # -> 11    (8 + 6 + 0 - 4)
best_sightseeing([1, 2])             # -> 2
```

**Think first:** split the score into `(values[i] + i)` and `(values[j] - j)`. For each `j`, which `i` is best?

**Hint:** pattern *Kadane-style best-so-far*: keep `best_left = max(values[i] + i)` over earlier `i`; score at `j` is `best_left + values[j] - j`.
