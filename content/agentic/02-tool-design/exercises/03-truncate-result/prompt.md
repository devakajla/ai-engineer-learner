# Keep tool results short

A tool that returns a whole 50,000-character web page fills the context window and costs money on **every** later step (the history is sent again each step). Good tools return **small, useful** results. When a result is too long, cut it and **tell the model** that it was cut, so it can ask for more.

Write `truncate_result(text, max_chars)`.

- If `len(text) <= max_chars`, return `text` unchanged.
- Otherwise return the first `max_chars` characters, then a new line, then the note `[truncated N more characters]`, where `N` is how many characters were cut.

```python
truncate_result("hello", 10)          # -> 'hello'
truncate_result("abcdefghij", 4)      # -> 'abcd\n[truncated 6 more characters]'
```

(The `\n` shows the line break.)

**Think first:** why is it better to say "truncated 6 more characters" than to cut silently? What can the model do with that note?

**Hint:** `text[:max_chars]` is the first part. `len(text) - max_chars` is what was cut.
