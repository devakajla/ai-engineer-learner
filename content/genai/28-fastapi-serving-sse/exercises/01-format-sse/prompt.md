# One server-sent event

**SSE** (server-sent events) is a simple way for a server to push text to a browser, piece by piece, over one open HTTP connection. Each piece is a little text block:

```
event: token
data: Hello

```

(There is an empty line at the end. It marks the end of one event.)

Write `format_sse(data, event=None)`. `data` is text.

Rules:
- If `event` is given, the first line is `"event: " + event`.
- Then one line `"data: " + line` for **each line** of `data` (split `data` on `"\n"`). An SSE `data:` line cannot hold a line break, so a multi-line text becomes several `data:` lines.
- Join the lines with `"\n"`, and finish with **two** line breaks: `"\n\n"`.

```python
format_sse("Hello", "token")   # -> 'event: token\ndata: Hello\n\n'
format_sse("a\nb")             # -> 'data: a\ndata: b\n\n'
format_sse("")                 # -> 'data: \n\n'
```
