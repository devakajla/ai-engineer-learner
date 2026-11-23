# Palindrome (recursion)

Write `is_palindrome(s)` that returns `True` if the string reads the same both ways, **using recursion**. The string has only lowercase letters.

```python
is_palindrome("level")    # -> True
is_palindrome("ab")       # -> False
```

**Think first:** if the first and last letters are different, you know the answer. If they match, what is left to check?

**Hint:** pattern *shrink from both ends*: `if len(s) < 2: return True`; `s[0] == s[-1] and is_palindrome(s[1:-1])`.
