# Flood fill

`image` is a list of lists of ints. Starting at cell `(sr, sc)`, change its colour and the colour of every cell **connected to it** (up, down, left, right) that has the **same original colour**, to `color`. Write `flood_fill(image, sr, sc, color)` that returns a **new** image; do not change the input.

```python
flood_fill([[1, 1, 0], [1, 0, 0], [1, 1, 1]], 1, 1, 2)    # -> [[1, 1, 2], [1, 2, 2], [1, 1, 1]]
flood_fill([[0, 0], [0, 0]], 0, 0, 0)                    # -> [[0, 0], [0, 0]]
```

**Think first:** if the new colour equals the old one, can a naive search run forever? What marks a cell as done?

**Hint:** pattern *grid DFS*: remember `old = image[sr][sc]`; search from `(sr, sc)` over cells equal to `old` using a `visited` set; paint a copy.
