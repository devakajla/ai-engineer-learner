# IPO: pick projects to grow capital

You start with capital `w`. There are projects; project `i` needs at least `capital[i]` to start and gives `profits[i]` (profit is added to your capital at once). You can do at most `k` projects. Write `max_capital(k, w, profits, capital)` that returns the **biggest final capital**.

```python
max_capital(2, 0, [1, 2, 3], [0, 1, 1])    # -> 4
max_capital(3, 0, [1, 2, 3], [0, 1, 2])    # -> 6
```

**Think first:** of all projects you can afford now, which one is best to take? Does taking it unlock more?

**Hint:** pattern *two-stage greedy with heap*: sort projects by needed capital; move every affordable project into a max-heap of profits (push `-profit`); take the best; repeat `k` times.
