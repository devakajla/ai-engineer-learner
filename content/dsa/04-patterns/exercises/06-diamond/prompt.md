# Diamond

Write `diamond(n)` that returns `2 * n - 1` rows: a pyramid of `n` rows followed by the pyramid upside down without repeating the widest row. Same spacing rules as `pyramid`, no trailing spaces.

```python
diamond(3)
# -> ['  *', ' ***', '*****', ' ***', '  *']
```

**Think first:** the bottom half is the top half reversed. Which row do you not repeat?

**Hint:** build the top as in `pyramid`, then loop `i` from `n - 1` down to `1` (`range(n - 1, 0, -1)`) for the bottom.
