# Fibonacci with memory

`fib(0) = 0`, `fib(1) = 1`, `fib(n) = fib(n - 1) + fib(n - 2)`. Write `fib(n)` that returns the n-th number. It must be fast for `n = 40`: remember answers you already computed in a dict.

```python
fib(10)    # -> 55
fib(40)    # -> 102334155
```

**Think first:** how many times does the plain recursion compute `fib(5)` when you ask for `fib(40)`? How can a dict stop that?

**Hint:** pattern *memoization*: pass or keep a dict `memo`; `if n in memo: return memo[n]`; store the result before returning.
