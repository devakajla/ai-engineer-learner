# First unique character

Write `first_unique_char(s)` that returns the index of the first character that appears only once. If there is none, return `-1`.

```python
first_unique_char("leetcode")   # -> 0
first_unique_char("aabbcd")     # -> 4
first_unique_char("aabb")       # -> -1
```

**Think first:** you need counts first, then a second pass in the original order.

**Hint:** counts dict, then `for i, ch in enumerate(s)`.
