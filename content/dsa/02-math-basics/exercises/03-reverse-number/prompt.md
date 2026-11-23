# Reverse a number

Write `reverse_number(n)` that returns the digits of a non-negative integer in reverse order, as an integer.

```python
reverse_number(1234)   # -> 4321
reverse_number(1200)   # -> 21
reverse_number(5)      # -> 5
```

**Think first:** reversing means the last digit becomes the first. Build the result one digit at a time: `result = result * 10 + digit`.

**Hint:** same peel-digits loop, plus a `result` variable.
