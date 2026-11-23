# Group words by length

Write `group_by_length(words)` that returns a dict: key is a word length, value is the list of words with that length, in the original order.

```python
group_by_length(["hi", "yo", "hey"])
# -> {2: ['hi', 'yo'], 3: ['hey']}
```

**Think first:** what is the key? What goes in the list?

**Hint:** `setdefault(len(w), []).append(w)`.
