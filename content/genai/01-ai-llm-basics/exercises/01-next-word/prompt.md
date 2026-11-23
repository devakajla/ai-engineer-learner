# Pick the next word

Write `next_word(word, table)`. The `table` maps a word to a dictionary of `{next word: chance}`.

Return the next word with the **highest chance**.

Rules:
- If `word` is not in `table`, return `None`.
- If its dictionary is empty, return `None`.
- If two words have the same top chance, return the one that comes first in the dictionary.

```python
table = {"I": {"like": 0.6, "am": 0.4}, "like": {"tea": 0.7, "coffee": 0.3}}

next_word("I", table)       # -> 'like'
next_word("like", table)    # -> 'tea'
next_word("tea", table)     # -> None
```
