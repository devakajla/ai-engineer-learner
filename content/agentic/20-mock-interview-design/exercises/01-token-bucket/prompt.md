# Design drill 1: a token-bucket rate limiter

**Asked as:** "How would you rate-limit users of an LLM API? Write the core of it."

A **token bucket** is the common answer. A bucket holds up to `capacity` tokens. Each request takes tokens out (`cost`, usually 1, but for LLM calls it can be the number of **LLM tokens** the request will use). Tokens **refill** at `rate` per second, but never above the capacity. If the bucket has enough tokens, the request is allowed. If not, it is refused (and you answer with HTTP 429 and a "retry after" time).

Write:

1. `new_bucket(rate_per_second, capacity, now=0.0)`: return `{"rate": rate_per_second, "capacity": capacity, "tokens": float(capacity), "last": now}`. A new bucket is full.
2. `allow(bucket, now, cost=1)`: first refill: `elapsed = max(0.0, now - bucket["last"])`, `tokens = min(capacity, tokens + elapsed * rate)`, and set `last = now`. Then, if `tokens >= cost`, subtract the cost and return `True`. Otherwise return `False` and **do not** change the tokens (except for the refill).

```python
bucket = new_bucket(1, 3)
[allow(bucket, 0.0) for _ in range(4)]
# -> [True, True, True, False]
```

**Think first:** a bucket allows a short **burst** and still limits the long-run rate. Which two numbers control the burst size and the average rate?

**Hint:** do the refill every time `allow` is called. No background timer is needed.
