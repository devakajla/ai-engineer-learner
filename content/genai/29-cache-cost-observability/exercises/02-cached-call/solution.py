import hashlib
import json


# Given from earlier exercises. Do not change these.
def cache_key(model, messages, temperature):
    payload = json.dumps(
        {"model": model, "messages": messages, "temperature": temperature},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def cached_call(cache, client, messages, model="qwen/qwen3.8-27b", temperature=0):
    key = cache_key(model, messages, temperature)
    if temperature == 0 and key in cache:
        return {"text": cache[key], "cached": True}
    response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    text = response.choices[0].message.content
    if temperature == 0:
        cache[key] = text
    return {"text": text, "cached": False}
