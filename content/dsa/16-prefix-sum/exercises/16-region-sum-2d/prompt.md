# Sum of a rectangle (2D)

`matrix` is a list of rows. Each query is `[r1, c1, r2, c2]`: the rectangle from row `r1` to `r2` and column `c1` to `c2` (all included). Write `region_sums(matrix, queries)` that returns the sum of each rectangle. Every query must be O(1) after one preparation.

```python
m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
region_sums(m, [[0, 0, 1, 1], [1, 1, 2, 2]])    # -> [12, 28]
```

**Think first:** how would you get a rectangle if you knew the sum of the rectangle from the top-left corner to any cell? (Big minus two sides plus the corner counted twice.)

**Hint:** pattern *2D prefix sum*: `P[i+1][j+1] = m[i][j] + P[i][j+1] + P[i+1][j] - P[i][j]`, with a row and a column of zeros in front.
