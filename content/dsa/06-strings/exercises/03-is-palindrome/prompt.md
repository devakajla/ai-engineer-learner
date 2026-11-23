# Palindrome string

Write `is_palindrome(s)` that returns `True` if `s` reads the same forwards and backwards, ignoring case and ignoring any character that is not a letter or digit.

```python
is_palindrome("Madam")                 # -> True
is_palindrome("A man, a plan, a canal: Panama")   # -> True
is_palindrome("hello")                 # -> False
```

**Think first:** first clean the text, then compare with its reverse.

**Hint:** loop with `isalnum()`, `lower()`, then `[::-1]`.
