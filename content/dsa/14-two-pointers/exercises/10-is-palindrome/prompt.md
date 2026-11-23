# Valid palindrome

Write `is_palindrome(s)` that returns `True` if `s` reads the same forwards and backwards when you look only at **letters and digits** and ignore upper/lower case.

```python
is_palindrome("A man, a plan, a canal: Panama")    # -> True
is_palindrome("race a car")                        # -> False
```

**Think first:** what should happen when the pointer meets a space or comma?

**Hint:** `left`/`right` from both ends. Skip while `not s[left].isalnum()`. Compare `s[left].lower()` with `s[right].lower()`.
