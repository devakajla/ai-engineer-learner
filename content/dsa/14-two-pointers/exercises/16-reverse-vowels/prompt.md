# Reverse vowels

Write `reverse_vowels(s)` that reverses only the **vowels** (`a e i o u`, upper or lower case) of `s`. All other characters stay where they are.

```python
reverse_vowels("hello")       # -> "holle"
reverse_vowels("leetcode")    # -> "leotcede"
```

**Think first:** what must each pointer do when it is **not** on a vowel?

**Hint:** strings cannot change, so `chars = list(s)`. Move `left` to the next vowel, `right` to the previous vowel, swap, move both. Return `"".join(chars)`.
