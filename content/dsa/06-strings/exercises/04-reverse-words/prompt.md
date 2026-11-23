# Reverse the words

Write `reverse_words(sentence)` that returns the words in reverse order, joined by a single space. Extra spaces in the input are ignored.

```python
reverse_words("the sky is blue")    # -> "blue is sky the"
reverse_words("  hello   world ")   # -> "world hello"
```

**Think first:** what does `split()` do with extra spaces?

**Hint:** `split()`, reverse the list, `" ".join(...)`.
