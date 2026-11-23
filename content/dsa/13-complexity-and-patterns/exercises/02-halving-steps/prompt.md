# Halving steps

Write `halving_steps(n)` for `n >= 1`. Count how many times you can do `n //= 2` until `n` becomes 1.

```python
halving_steps(8)      # -> 3     (8 -> 4 -> 2 -> 1)
halving_steps(10)     # -> 3     (10 -> 5 -> 2 -> 1)
```

**Think first:** what should the answer be when `n` is already 1?

**Hint:** a `while n > 1` loop with a step counter. This count is the "log n" of the lesson.
