# Fit the context budget

The prompt has a size limit. Write `fit_hits(hits, max_words)`. `hits` come best first, each with `"text"`.

Rules:
- Take hits in order while the **total words** stay at or under `max_words`. Words are counted with `len(text.split())`.
- Stop at the **first** hit that does not fit. Do not skip it to pick a later, smaller one (that would put a weaker hit before a better one).
- Return the chosen hits as a list (same dictionaries, same order). Do not change the input.
- `max_words <= 0` or no hits give `[]`.

```python
hits = [{"text": "a b c"}, {"text": "d e"}, {"text": "f"}]
fit_hits(hits, 5)   # -> [{'text': 'a b c'}, {'text': 'd e'}]
fit_hits(hits, 4)   # -> [{'text': 'a b c'}]       (the second needs 2 more, so stop)
fit_hits(hits, 2)   # -> []
```

**Think first:** what would you do in production where words are not tokens?
