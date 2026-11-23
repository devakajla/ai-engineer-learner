# Minimum arrows to burst balloons

Each balloon is `[x_start, x_end]` on a line (closed). An arrow shot at `x` bursts every balloon with `x_start <= x <= x_end`. Write `min_arrows(balloons)` that returns the fewest arrows needed to burst all balloons.

```python
min_arrows([[10, 16], [2, 8], [1, 6], [7, 12]])    # -> 2
min_arrows([[1, 2], [3, 4], [5, 6], [7, 8]])       # -> 4
```

**Think first:** shoot as far **right** as you can while still hitting the balloon that ends first. Which other balloons does that arrow burst?

**Hint:** pattern *greedy by end*: sort by end; shoot at the first end; skip every balloon whose start is `<=` that arrow; then shoot again.
