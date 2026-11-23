# A stream that can fail halfway

Streams break: the network drops, the provider returns an error in the middle. The browser already got part of the text. You cannot change the HTTP status any more (the `200` was sent). So you tell the browser with an **error event**.

In the starter: `format_sse` and `chunk_text`. Write `sse_safe(stream, event="token")`. It works like `sse_events` (exercise 3), and adds error handling:

- Loop over the stream inside `try`. Add a token event for each non-empty text, as before.
- If **any exception** is raised while you loop, add `format_sse("stream failed: " + str(error), "error")` and return the events so far. Do **not** add the `done` event in that case.
- If the stream ends normally, add the `done` event as before.

```python
# the stream gives "a", then raises RuntimeError("boom")
sse_safe(stream)
# -> ['event: token\ndata: a\n\n', 'event: error\ndata: stream failed: boom\n\n']
```

**Think first:** why can't you just return an HTTP 500 here?
