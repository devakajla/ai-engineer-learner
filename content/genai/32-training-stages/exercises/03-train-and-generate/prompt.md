# Train a tiny model and write with it

Put it together. Train on text (count, then turn counts into chances), then write a sentence the way an LLM does.

The three helpers from earlier are **given** in `starter.py`: `count_pairs`, `to_chances` and `generate`. Do not change them.

Write `train_and_generate(text, start, max_words)`:
1. Train a table from `text`: first count the pairs, then turn the counts into chances.
2. Make the sentence with `generate(start, table, max_words)`.
3. Return the sentence.

Rules:
- `start` may have capital letters. The table is lowercase, so make `start` lowercase before you use it.
- If `start` is not a word in the training text, return the lowercase `start` alone.

**Think first:** In which order must the three steps run, and what does each one take as input?

**Hint:** The answer is short. Each helper gives the next one its input.

```python
text = "the cat sat on the mat the cat ran"

train_and_generate(text, "the", 4)    # -> 'the cat sat on'
train_and_generate(text, "The", 2)    # -> 'the cat'
train_and_generate(text, "dog", 5)    # -> 'dog'
```
