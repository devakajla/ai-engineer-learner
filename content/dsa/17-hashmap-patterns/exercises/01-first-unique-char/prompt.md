# First unique character

Write `first_unique_index(s)` that returns the **index** of the first character that appears **exactly once** in `s`. Return `-1` if there is none.

```python
first_unique_index("loveleetcode")    # -> 2
first_unique_index("aabb")            # -> -1
```

**Think first:** can you know how many times a letter appears before you decide? How many passes do you need?

**Hint:** pattern *counter-dict*: pass 1 counts every letter, pass 2 returns the first index whose count is `1`.
