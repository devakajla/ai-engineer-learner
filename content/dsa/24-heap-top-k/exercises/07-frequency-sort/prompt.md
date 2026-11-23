# Sort characters by frequency

Write `frequency_sort(s)` that returns the string with characters grouped, **most frequent first**. For equal counts, the **smaller character** first.

```python
frequency_sort("tree")      # -> "eert"
frequency_sort("cccaaa")    # -> "aaaccc"
```

**Think first:** count first. What do you push so the heap pops the highest count first, then the smallest letter?

**Hint:** pattern *count + heap*: push `(-count, char)`; pop all and append `char * count`.
