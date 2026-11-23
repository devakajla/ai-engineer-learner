# Longest palindrome you can build

Write `longest_palindrome(s)` that returns the length of the longest palindrome you can make using the letters of `s` (each letter once, any order). Upper and lower case are different letters.

```python
longest_palindrome("abccccdd")    # -> 7   ("dccaccd")
longest_palindrome("a")           # -> 1
```

**Think first:** in a palindrome, letters come in pairs around the middle. How many letters can sit in the middle?

**Hint:** pattern *counter-dict (pairs)*: add `count // 2 * 2` for every letter; if any letter has an odd count, add `1` for the middle.
