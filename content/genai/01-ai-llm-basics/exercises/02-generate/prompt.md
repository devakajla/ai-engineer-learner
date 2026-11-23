# Generate a sentence

Write `generate(start, table, max_words)`. It builds a sentence the way an LLM does: repeat "find the most likely next word and add it".

The `table` maps a word to a dictionary of `{next word: chance}`.

Your `next_word` function from the previous exercise is **given** in `starter.py`. Use it. Do not change it.

Rules:
- The sentence starts with `start`.
- Look at the **last** word. Add the word with the highest chance after it.
- Stop when there are `max_words` words, or when the last word has no next word.
- Return the words joined by single spaces.
- If two words tie, use the one that comes first in the dictionary.

**Think first:** Which word do you look at each time round the loop, and when must the loop stop?

**Hint:** A `while` loop and `next_word`.

```python
table = {"I": {"like": 0.6, "am": 0.4}, "like": {"tea": 0.7, "coffee": 0.3}}

generate("I", table, 5)    # -> 'I like tea'
generate("I", table, 2)    # -> 'I like'
generate("tea", table, 3)  # -> 'tea'
```
