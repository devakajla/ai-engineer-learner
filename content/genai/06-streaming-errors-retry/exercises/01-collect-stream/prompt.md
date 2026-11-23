# Collect a streamed answer

When you call the model with `stream=True`, you get many small chunks. Write `collect_stream(stream)` to join them into the full text.

Each chunk has `chunk.choices`, a list. The text piece is `chunk.choices[0].delta.content`.

Rules:
- `stream` is anything you can loop over with `for`.
- Skip chunks where `choices` is an empty list.
- Skip pieces that are `None` or an empty string.
- Return all the pieces joined into one string.

```python
collect_stream(stream)
# pieces: "Hel", None, "lo" -> 'Hello'

collect_stream([])
# -> ''
```
