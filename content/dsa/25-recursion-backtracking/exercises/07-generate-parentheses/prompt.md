# Generate parentheses

Write `generate_parentheses(n)` that returns **all** valid strings with `n` pairs of `()`. Any order.

```python
generate_parentheses(1)    # -> ["()"]
generate_parentheses(2)    # -> ["(())", "()()"]   (any order)
```

**Think first:** when may you add `(`? When may you add `)`? What do you count?

**Hint:** pattern *backtracking with rules*: keep `open_used` and `close_used`; add `(` if `open_used < n`; add `)` if `close_used < open_used`; when the length is `2 * n` save it.
