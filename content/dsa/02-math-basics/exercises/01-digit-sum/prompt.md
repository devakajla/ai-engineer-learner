# Sum of digits

Write `digit_sum(n)` that returns the sum of the digits of a non-negative integer.

```python
digit_sum(1234)    # -> 10
digit_sum(9)       # -> 9
digit_sum(0)       # -> 0
```

**Think first:** how do you get the last digit? How do you drop it?

**Hint:** `% 10` and `// 10` in a `while` loop.
