# Reverse a string (recursion)

Write `reverse(s)` that returns the string reversed **using recursion** (no slicing like `s[::-1]`, no `reversed`).

```python
reverse("abc")    # -> "cba"
reverse("")       # -> ""
```

**Think first:** if you reverse everything except the first letter, where does the first letter go?

**Hint:** pattern *base case + combine*: `if s == "": return ""`; else `reverse(s[1:]) + s[0]`.
