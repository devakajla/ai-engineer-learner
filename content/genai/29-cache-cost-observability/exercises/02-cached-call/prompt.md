# Use the cache

In the starter: `cache_key` (exercise 1), with `json` and `hashlib`.

Write `cached_call(cache, client, messages, model="qwen/qwen3.8-27b", temperature=0)`. `cache` is a dictionary `{key: text}`. **Change it in place.**

Rules:
1. Make the key with `cache_key(model, messages, temperature)`.
2. Only when `temperature == 0`: if the key is in the cache, return `{"text": cache[key], "cached": True}` and make **no** model call. (At temperature above 0 the answers are meant to differ, so we never reuse them.)
3. Otherwise call `client.chat.completions.create(model=model, messages=messages, temperature=temperature)` and take `response.choices[0].message.content`.
4. Only when `temperature == 0`, store the text in the cache.
5. Return `{"text": text, "cached": False}`.

```python
cached_call(cache, client, msgs)   # first time  -> {'text': 'Hello!', 'cached': False}   (1 model call)
cached_call(cache, client, msgs)   # second time -> {'text': 'Hello!', 'cached': True}    (no call)
```

**Think first:** what goes wrong if two different users share the cache for a prompt that holds their private data?
