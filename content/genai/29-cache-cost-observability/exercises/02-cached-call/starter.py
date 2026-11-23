import hashlib
import json


# Given from earlier exercises. Do not change these.
def cache_key(model, messages, temperature):
    payload = json.dumps(
        {"model": model, "messages": messages, "temperature": temperature},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Your task:
def cached_call(cache, client, messages, model="qwen/qwen3.8-27b", temperature=0):
    ...
