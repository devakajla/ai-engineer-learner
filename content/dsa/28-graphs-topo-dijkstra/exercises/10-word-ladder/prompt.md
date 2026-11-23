# Word ladder

Change one letter at a time to turn `begin` into `end`. Every new word must be in `words`. Write `ladder_length(begin, end, words)` that returns the **number of words** in the shortest sequence (counting `begin` and `end`), or `0` if there is none. `begin` does not need to be in `words`.

```python
ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])    # -> 5   (hit, hot, dot, dog, cog)
ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"])           # -> 0
```

**Think first:** each word is a node; two words are neighbours if they differ in exactly one letter. What kind of path do you want?

**Hint:** pattern *BFS on implicit graph*: queue of `(word, length)`; for each position try the 26 letters, and keep results that are in the word set and unvisited. Remove words from the set as you visit them.
