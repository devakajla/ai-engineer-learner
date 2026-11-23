# N-Queens: count the solutions

Place `n` queens on an `n x n` chess board so that no two attack each other (same row, same column or same diagonal). Write `count_queens(n)` that returns **how many** different ways there are.

```python
count_queens(4)    # -> 2
count_queens(1)    # -> 1
```

**Think first:** put one queen per row. For each row, which columns are still allowed? What do two queens on the same diagonal have in common (`row - col` or `row + col`)?

**Hint:** pattern *backtracking with sets*: keep sets `cols`, `diag1` (`r - c`) and `diag2` (`r + c`); `go(r)`: for each column `c` not blocked, add to the sets, `go(r + 1)`, remove. When `r == n` count one.
