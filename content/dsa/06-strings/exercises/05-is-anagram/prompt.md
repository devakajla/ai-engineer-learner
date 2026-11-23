# Anagram check

Write `is_anagram(a, b)` that returns `True` if the two words use exactly the same letters the same number of times. Ignore case.

```python
is_anagram("listen", "silent")   # -> True
is_anagram("abc", "abd")         # -> False
is_anagram("Aab", "baa")         # -> True
```

**Think first:** if you sort the letters of both words, what must be true?

**Hint:** `sorted(word.lower())` returns a list of characters.
