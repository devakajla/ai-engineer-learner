# Top characters

Write `top_chars(text, n)` that returns a list of the `n` most frequent characters as `(char, count)` tuples, most frequent first. Ignore spaces and compare case-insensitively (use lower case). If two characters have the same count, the one that comes first alphabetically goes first. If there are fewer than `n` different characters, return all of them.

```python
top_chars("Hello World", 2)   # -> [("l", 3), ("o", 2)]
top_chars("aabb", 5)          # -> [("a", 2), ("b", 2)]
top_chars("", 3)              # -> []
```
