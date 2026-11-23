# Read one streaming chunk

When you stream from the model (lesson 6), you get many small **chunks**. A chunk looks like this: `chunk.choices[0].delta.content` holds a piece of text. But watch out:

- The text can be `None` (for example in the first or the last chunk).
- `chunk.choices` can be an **empty list** (some providers send a final chunk with usage data only).

`format_sse` (exercise 1) is in the starter. Write `chunk_text(chunk)`:

- If `chunk.choices` is empty, return `""`.
- Otherwise take `chunk.choices[0].delta.content`. If it is `None`, return `""`. Else return it.

```python
chunk_text(chunk_with("Hel"))   # -> 'Hel'
chunk_text(chunk_with(None))    # -> ''
chunk_text(chunk_with_no_choices)   # -> ''
```
