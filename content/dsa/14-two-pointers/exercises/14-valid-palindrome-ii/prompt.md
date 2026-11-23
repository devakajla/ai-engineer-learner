# Valid palindrome II

Write `valid_palindrome_ii(s)` that returns `True` if `s` is a palindrome **or becomes one after deleting at most one character**. `s` has only lowercase letters.

```python
valid_palindrome_ii("abca")    # -> True     (delete 'c' or 'b')
valid_palindrome_ii("abc")     # -> False
```

**Think first:** when the two ends differ, how many choices do you have, and what do you check after each?

**Hint:** opposite ends. On a mismatch, check the string without `s[left]` **or** without `s[right]` with a small helper that checks `s[i..j]` for a palindrome.
