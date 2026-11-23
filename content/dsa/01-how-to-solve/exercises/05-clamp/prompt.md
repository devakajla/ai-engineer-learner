# Clamp a number

Write `clamp(x, low, high)` that returns `x` if it is between `low` and `high`. If `x` is below `low`, return `low`. If above `high`, return `high`.

```python
clamp(5, 0, 10)     # -> 5
clamp(-3, 0, 10)    # -> 0
clamp(99, 0, 10)    # -> 10
```

**Think first:** how many different cases are there? Which one is the "normal" case?

**Hint:** early `return` inside two `if`s, then `return x`.
