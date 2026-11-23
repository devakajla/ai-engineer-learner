# Maximum vowels in a window

Write `max_vowels(s, k)` that returns the largest number of vowels (`a e i o u`) in any substring of length `k`. `s` has lowercase letters and `1 <= k <= len(s)`.

```python
max_vowels("abciiidef", 3)    # -> 3   ("iii")
max_vowels("leetcode", 3)     # -> 2
```

**Think first:** what number do you update when one letter enters and one leaves?

**Hint:** pattern *fixed window*: `count += is_vowel(new) - is_vowel(old)`. A `"aeiou"` string works for the check.
