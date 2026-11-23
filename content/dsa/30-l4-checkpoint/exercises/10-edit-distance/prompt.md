# Edit distance

One edit is: insert a letter, delete a letter, or replace a letter. Write `edit_distance(a, b)` that returns the fewest edits needed to turn `a` into `b`.

```python
edit_distance("horse", "ros")    # -> 3
edit_distance("", "abc")         # -> 3
```

**Think first:** compare the last letters. If equal, nothing to pay. If not, which three smaller problems can you try?

**Hint:** pattern *2D DP table*: `dp[i][j]` = edits for the first `i` letters of `a` and `j` of `b`; equal: `dp[i-1][j-1]`; else `1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`. First row and column are the base cases.
