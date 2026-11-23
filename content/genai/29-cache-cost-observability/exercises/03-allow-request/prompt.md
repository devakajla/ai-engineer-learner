# A rate limit

A **rate limit** says: at most `limit` requests in any `window` seconds. It protects your wallet and your server from one greedy user (or a bug in a loop). The simplest kind is a **sliding window**: remember the times of the recent requests.

Write `allow_request(timestamps, now, limit, window)`.

- `timestamps`: the times (numbers, in seconds) of this user's earlier allowed requests.
- `now`: the time of this request.

Rules:
1. Keep only the **recent** times: those `t` with `now - window < t <= now`. Older ones are forgotten.
2. If fewer than `limit` recent times remain, the request is **allowed**. Return `{"allowed": True, "timestamps": recent + [now], "retry_after": 0}`.
3. Otherwise it is **blocked**. Return `{"allowed": False, "timestamps": recent, "retry_after": recent[0] + window - now}`. `retry_after` tells the client how many seconds to wait: the oldest recent request leaves the window at `recent[0] + window`. (The timestamps are in order, oldest first.)
4. Do not change the list you were given.

```python
allow_request([], 100, 2, 60)           # -> {'allowed': True, 'timestamps': [100], 'retry_after': 0}
allow_request([100, 110], 120, 2, 60)   # -> {'allowed': False, 'timestamps': [100, 110], 'retry_after': 40}
allow_request([100, 110], 161, 2, 60)   # -> {'allowed': True, 'timestamps': [110, 161], 'retry_after': 0}
```

**Think first:** what does the client do with HTTP 429 and a `Retry-After` header? (Lesson 6.)
