# Turn a model stream into SSE events

In the starter: `format_sse` and `chunk_text`.

Write `sse_events(stream, event="token")`. `stream` is anything you can loop over that gives chunks. Return a **list** of SSE texts:

1. For every chunk, get its text with `chunk_text`. If the text is empty, skip the chunk. Otherwise add `format_sse(text, event)`.
2. At the end add one last event that tells the browser the stream is finished: `format_sse("[DONE]", "done")`.

```python
# the stream gives "Hel", None, "lo"
sse_events(stream)
# -> ['event: token\ndata: Hel\n\n', 'event: token\ndata: lo\n\n', 'event: done\ndata: [DONE]\n\n']
```

**Think first:** why does the browser need a final `done` event?
