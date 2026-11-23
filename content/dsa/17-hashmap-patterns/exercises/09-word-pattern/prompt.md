# Word pattern

`pattern` is a string of letters and `text` is words separated by one space. Write `word_pattern(pattern, text)` that returns `True` if the words follow the pattern: each letter stands for exactly one word and each word for exactly one letter.

```python
word_pattern("abba", "dog cat cat dog")     # -> True
word_pattern("abba", "dog dog dog dog")     # -> False
```

**Think first:** this is exercise 08 with words instead of letters. What if the counts differ?

**Hint:** pattern *two dicts*: `letter -> word` and `word -> letter`. Use `text.split()`.
