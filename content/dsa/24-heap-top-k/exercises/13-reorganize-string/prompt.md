# Reorganize a string

Write `reorganize(s)` that rearranges the letters so **no two neighbours are equal**. Return any valid string, or `""` if impossible.

```python
reorganize("aab")    # -> "aba"
reorganize("aaab")   # -> ""
```

**Think first:** which letter is the most dangerous? Should you place it first?

**Hint:** pattern *max-heap, hold back one*: pop the most frequent letter, append it, then put the **previous** letter back into the heap (if it still has copies). The result is valid if its length equals `len(s)`.
