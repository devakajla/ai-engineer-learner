# Alphabet order from words

`words` is a list of words sorted by an unknown alphabet order. Write `alien_order(words)` that returns one string with the letters in a valid order, or `""` if the list is impossible. Use all letters that appear. If there are several valid orders, the **smallest in normal alphabetical order** must be returned (take the smallest available letter each time).

```python
alien_order(["wrt", "wrf", "er", "ett", "rftt"])    # -> "wertf"
alien_order(["z", "x", "z"])                        # -> ""
```

**Think first:** comparing two neighbouring words, the first different letter gives one rule "a before b". What do you build from the rules?

**Hint:** pattern *topological sort*: edges from the first differing letters of neighbouring words; Kahn with a heap (smallest letter first). If a word is a longer prefix of the word after it (like `"ab"` then `"a"`) the input is invalid.
