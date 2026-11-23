# Count digits

Write `count_digits(n)` that returns how many digits a non-negative integer has. `0` has one digit.

```python
count_digits(1234)   # -> 4
count_digits(7)      # -> 1
count_digits(0)      # -> 1
```

**Think first:** the loop for `0` never runs. How do you handle that?

**Hint:** do not convert to a string; use `// 10`.
