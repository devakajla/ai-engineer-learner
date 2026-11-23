# Palindrome check

Write `is_palindrome(text)` that returns `True` if `text` reads the same forwards and backwards, **ignoring case and spaces**.

```python
is_palindrome("racecar")                 # -> True
is_palindrome("Never odd or even")       # -> True
is_palindrome("python")                  # -> False
is_palindrome("")                        # -> True
```

Hint: clean the string first (`replace`, `lower`), then compare it with its reverse.
