# Allowed complexity

Write `allowed_complexity(n)` that returns the **slowest** complexity (as a string) that fits in about 10⁸ steps for input size `n`. Use this table:

| n up to | answer |
| --- | --- |
| 10 | `"O(n!)"` |
| 20 | `"O(2^n)"` |
| 500 | `"O(n^3)"` |
| 5000 | `"O(n^2)"` |
| 10**6 | `"O(n log n)"` |
| 10**8 | `"O(n)"` |
| bigger | `"O(log n)"` |

```python
allowed_complexity(1000)      # -> "O(n^2)"
allowed_complexity(10**5)     # -> "O(n log n)"
```

**Think first:** which `if` should you check first, the smallest limit or the biggest?

**Hint:** a chain of `if n <= ...: return ...`, smallest limit first. This is the *early exit* pattern.
