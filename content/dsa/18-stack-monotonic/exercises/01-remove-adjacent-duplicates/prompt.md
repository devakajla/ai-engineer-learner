# Remove adjacent duplicates

Write `remove_adjacent_duplicates(s)`. Repeatedly delete **two equal letters that sit next to each other**, until there are none. Return the final string.

```python
remove_adjacent_duplicates("abbaca")    # -> "ca"   (bb, then aa)
remove_adjacent_duplicates("azxxzy")    # -> "ay"
```

**Think first:** after you delete a pair, which two letters become neighbours? Which letter do you need to look at: the newest one kept?

**Hint:** pattern *stack of kept letters*: if `s[i]` equals the top, pop; else push. The answer is the stack joined.
