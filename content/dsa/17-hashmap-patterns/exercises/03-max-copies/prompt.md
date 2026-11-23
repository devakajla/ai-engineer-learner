# How many copies of a word

Write `max_copies(text, word)` that returns how many times you can build `word` using the letters of `text`. Each letter of `text` can be used once.

```python
max_copies("loonbalxballpoon", "balloon")    # -> 2
max_copies("leetcode", "balloon")            # -> 0
```

**Think first:** a word needs some letters twice (like `l` and `o` in "balloon"). For each needed letter, how many copies can `text` pay for? Which letter is the bottleneck?

**Hint:** pattern *counter-dict (need vs have)*: for every letter in `word`, `have // need`; the answer is the smallest of these.
