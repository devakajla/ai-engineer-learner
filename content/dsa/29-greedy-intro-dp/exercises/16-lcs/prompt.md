# Longest common subsequence

Write `lcs_length(a, b)` that returns the length of the longest subsequence that appears (in order, gaps allowed) in **both** strings.

```python
lcs_length("abcde", "ace")    # -> 3
lcs_length("abc", "def")      # -> 0
```

**Think first:** compare the last characters. If they match, what is left to solve? If not, which two smaller problems do you try?

**Hint:** pattern *2D DP table*: `dp[i][j]` for the first `i` letters of `a` and `j` of `b`; match: `dp[i-1][j-1] + 1`; else `max(dp[i-1][j], dp[i][j-1])`.
