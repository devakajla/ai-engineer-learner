# A key for the cache

If two requests are **exactly the same**, the answer can be the same, so you can reuse it and save money and time. First you need a **key**: a short code that is equal for equal requests and different for different ones.

Write `cache_key(model, messages, temperature)`. `import json` and `import hashlib` are in the starter.

Rules:
1. Put the three values in a dictionary with the keys `"model"`, `"messages"`, `"temperature"`.
2. Turn it into text with `json.dumps(..., sort_keys=True)`. (`sort_keys=True` makes the text the same even if the keys were written in another order.)
3. Return `hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]`.

```python
k1 = cache_key("m", [{"role": "user", "content": "hi"}], 0)
k2 = cache_key("m", [{"content": "hi", "role": "user"}], 0)
k1 == k2     # -> True   (the order of keys inside a message does not matter)
len(k1)      # -> 16
cache_key("m", [{"role": "user", "content": "hi"}], 0.5) == k1    # -> False
```
