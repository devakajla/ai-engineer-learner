# Surrounded regions

`board` is a list of strings of `"X"` and `"O"`. Capture every region of `"O"` that is **completely surrounded** by `"X"` (an `O` region touching the border cannot be captured). Write `solve(board)` that returns a **new** board (list of strings) where captured `O`s became `X`. Connections are up, down, left, right.

```python
solve(["XXXX", "XOOX", "XXOX", "XOXX"])    # -> ["XXXX", "XXXX", "XXXX", "XOXX"]
solve(["X"])                               # -> ["X"]
```

**Think first:** it is easier to find the `O`s that **survive**. Where must a surviving `O` region touch?

**Hint:** pattern *flood from the border*: start a search from every border `O`; mark everything reachable as safe; then turn all unmarked `O` into `X`.
