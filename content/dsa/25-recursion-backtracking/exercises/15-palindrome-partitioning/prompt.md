# Palindrome partitioning

Write `partition(s)` that cuts `s` into pieces so that **every piece is a palindrome**. Return all ways as lists of strings. Any order.

```python
partition("aab")    # -> [["a", "a", "b"], ["aa", "b"]]   (any order)
partition("a")      # -> [["a"]]
```

**Think first:** choose where the first piece ends. Which choices are allowed? What is left to solve?

**Hint:** pattern *choose a cut*: `go(start)`: for `end` in `start+1..len(s)`: if `s[start:end]` is a palindrome, append it, `go(end)`, pop. When `start == len(s)` save.
