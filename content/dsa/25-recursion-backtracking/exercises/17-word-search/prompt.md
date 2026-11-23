# Word search in a grid

`board` is a list of strings (all the same length). Write `exist(board, word)` that returns `True` if `word` can be built from letters of **neighbouring cells** (up, down, left, right), **without using the same cell twice**.

```python
board = ["ABCE", "SFCS", "ADEE"]
exist(board, "ABCCED")    # -> True
exist(board, "ABCB")      # -> False
```

**Think first:** from a cell, which 4 cells can you go to next? How do you stop yourself from reusing a cell, and how do you free it again?

**Hint:** pattern *grid backtracking*: try every start cell; `go(r, c, i)`: check bounds, letter and "not used"; mark used; try 4 directions with `i + 1`; **unmark** before returning.
