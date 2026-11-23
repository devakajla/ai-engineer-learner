# Find all anagrams

Write `find_anagrams(s, p)` that returns a list of **start indexes** of every substring of `s` that is an anagram of `p` (same letters, same counts, any order). Return the indexes in increasing order.

```python
find_anagrams("cbaebabacd", "abc")    # -> [0, 6]
find_anagrams("abab", "ab")           # -> [0, 1, 2]
```

**Think first:** every good window has exactly `len(p)` letters. What do you compare at each step?

**Hint:** pattern *fixed window + counter-dict*: keep the window's counts; add the new letter, remove the old one (delete keys that hit 0), compare dicts with `==`.
