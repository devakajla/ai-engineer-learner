# A fingerprint for a document

To know if a document changed, compare a short **fingerprint** (a hash) instead of the whole text. A **hash function** turns any text into a short, fixed-size code. The same text always gives the same code, and a different text almost surely gives a different code.

Write `content_hash(text)`.

Rules:
- First normalize the text: `" ".join(text.split())`. So a change in spaces or line breaks only does **not** change the hash.
- Return `hashlib.sha256(normal.encode("utf-8")).hexdigest()[:16]` (the first 16 characters).
- `import hashlib` is in the starter.

```python
content_hash("Hello  world")      # the same as
content_hash("Hello\nworld")      # -> both give the same 16-character text
content_hash("Hello there") != content_hash("Hello world")   # -> True
len(content_hash(""))             # -> 16
```
