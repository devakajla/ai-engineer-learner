# First n Fibonacci numbers

Write `fibonacci(n)` that returns a list with the first `n` Fibonacci numbers, starting `0, 1, 1, 2, 3, 5 ...`.

```python
fibonacci(6)   # -> [0, 1, 1, 2, 3, 5]
fibonacci(1)   # -> [0]
fibonacci(0)   # -> []
```

**Think first:** each number is the sum of the previous two. How many variables do you need to remember?

**Hint:** two variables `a, b = 0, 1`; update with `a, b = b, a + b`.
