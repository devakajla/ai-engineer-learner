# Make a data URL

A local picture cannot be sent as a file path. Turn its bytes into a **data URL**.

Write `data_url(mime, data)`. `mime` is the type of the file (like `"image/png"`). `data` is the file as **bytes**.

Rules:
- Return `"data:" + mime + ";base64," + <base64 text of data>`.
- Use the `base64` module: `base64.b64encode(data).decode()`.
- If `data` is empty (`b""`), raise `ValueError("no data")`.

```python
data_url("image/png", b"hi")     # -> 'data:image/png;base64,aGk='
data_url("image/jpeg", b"hello") # -> 'data:image/jpeg;base64,aGVsbG8='
data_url("image/png", b"")       # raises ValueError: no data
```
