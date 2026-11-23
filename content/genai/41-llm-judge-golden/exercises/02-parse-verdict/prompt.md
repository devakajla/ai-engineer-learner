# Read the judge's verdict

Models often add words around the JSON ("Sure! Here is my grade: {...}"). Read the verdict safely.

Write `parse_verdict(reply)`. `import json` is in the starter.

Rules:
1. Find the first `{` and the last `}` in the reply. If one is missing, return `None`. Take the text between them (including both).
2. Parse it with `json.loads`. Invalid JSON: return `None`. Not a dictionary: return `None`.
3. `"score"` must be an **int** from 1 to 5. A `bool`, a float, a text, a missing score or another number: return `None`. (In Python `True` is an `int`, so check for `bool` first!)
4. `"reason"` is optional. If it is missing or not a text, use `""`.
5. Return `{"score": score, "reason": reason}`.

```python
parse_verdict('Sure! {"score": 4, "reason": "ok"} Done.')   # -> {'score': 4, 'reason': 'ok'}
parse_verdict('{"score": 9}')                               # -> None
parse_verdict("no json here")                               # -> None
```
