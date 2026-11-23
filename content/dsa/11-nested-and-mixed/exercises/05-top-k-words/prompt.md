# Top k words

Write `top_k_words(text, k)` that returns the `k` most frequent words as a list. Words are split on whitespace and compared in lowercase. For equal counts, sort A to Z. If there are fewer than `k` distinct words, return all of them.

```python
top_k_words("the cat the dog the end cat", 2)   # -> ['the', 'cat']
top_k_words("b a b a c", 2)                     # -> ['a', 'b']
```

**Think first:** this is three steps: split and count, build pairs, sort with a two-part key.

**Hint:** counts dict, then a list of pairs `(-count, word)`. Sorting pairs sorts by count (high first), then word (A to Z). Take the words from the first `k` pairs.
