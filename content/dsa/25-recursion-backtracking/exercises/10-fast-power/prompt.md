# Fast power

Write `fast_power(x, n)` that returns `x ** n` for an integer `n >= 0`, **using recursion** and only about `log2(n)` calls (do not multiply `n` times). Do not use `**` or `pow`.

```python
fast_power(2, 10)    # -> 1024
fast_power(5, 0)     # -> 1
```

**Think first:** `x^10 = (x^5) * (x^5)`. How much work do you save if you compute `x^5` only once?

**Hint:** pattern *divide in half*: `half = fast_power(x, n // 2)`; result is `half * half`, times `x` if `n` is odd.
