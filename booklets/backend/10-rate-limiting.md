# 10. Rate limiting

A **rate limit** says: "you may make at most N requests in a time window". When a client goes over, the server answers `429 Too Many Requests`.

Real life: a water tap that gives only so much per minute, so one person cannot empty the tank.

## Why limit?

| Reason | Example |
| --- | --- |
| Protect the server | a buggy loop sends 50,000 requests a second |
| Stop abuse | someone tries a million passwords on `/login` |
| Be fair | one heavy user should not slow down everyone |
| Control cost | every LLM call costs money |
| Respect others | your own calls to a third-party API have limits too |

## The four main algorithms

### 1. Fixed window

Count requests in each clock window (for example each minute). At the start of the next window, the count is `0`.

```
limit = 100 per minute
12:00:00 - 12:00:59 -> count up to 100, then block
12:01:00            -> reset to 0
```

Simple and cheap. Weakness: **a burst at the edge**. A client sends 100 requests at 12:00:59 and 100 more at 12:01:00. That is 200 requests in two seconds, and no rule is broken.

### 2. Sliding window

Look at the **last 60 seconds** from *now*, not at the clock minute. Count the requests in that moving window.

- **Sliding log**: store each timestamp. Exact, but uses more memory.
- **Sliding counter**: a cheaper approximation using the previous and the current window.

It fixes the edge burst. Costs a little more.

### 3. Token bucket

Picture a bucket that holds tokens. Tokens are added at a steady rate (say 10 per second), up to the bucket size (say 50). Each request takes one token. No token, no entry.

@@ flow | Figure 10.1: the token bucket.
Refill|+10 tokens per second|green -> Bucket|holds at most 50 tokens|yellow -one token each-> Request|allowed if a token exists;else 429|blue
@@ end

Good: it allows **short bursts** (up to the bucket size) while keeping the **average rate** fixed. This matches real traffic well. It is the most popular choice.

### 4. Leaky bucket

Requests drop into a bucket, and leak out at a fixed speed. If the bucket overflows, extra requests are dropped. The output is smooth and steady. Good for protecting a downstream system that wants an even flow.

| Algorithm | Allows bursts? | Memory | Accuracy | Notes |
| --- | --- | --- | --- | --- |
| Fixed window | edge bursts | tiny | low | simplest |
| Sliding window | no | medium | high | smooth |
| **Token bucket** | **yes, controlled** | tiny | good | the usual choice |
| Leaky bucket | no | tiny | good | smooth output |

## What do you limit by?

The **key** decides who shares a counter.

| Key | Use |
| --- | --- |
| IP address | anonymous traffic, login page (but many users share one IP behind an office network) |
| User id | logged-in users |
| API key | paying customers, with different plans |
| Endpoint | stricter on `/login`, looser on `/health` |

Often you combine them: `user:7:POST:/chat`.

## Where to enforce it

| Place | Pros | Cons |
| --- | --- | --- |
| API gateway / Nginx / CDN | stops traffic before your code runs | less flexible rules |
| In the app (with Redis) | any rule you like, per user or plan | uses your app's time |
| Both | strong defence | more to set up |

With several app servers, the counter must be **shared**, so use **Redis**. A counter in each server's memory would let a user get N times the limit.

## A Redis fixed-window limiter

```
INCR rl:user:7:202611220915      -- add 1, create the key at 0 if missing
EXPIRE rl:user:7:202611220915 60 -- only needed on the first hit
-- if the returned count > 100 -> reject with 429
```

`INCR` is **atomic**: even if 1,000 requests arrive at once, Redis counts each one correctly. The key includes the minute, so it changes every minute.

## Telling the client

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1764666000
```

A good client reads `Retry-After` and waits. Good APIs always send these headers.

## The other side: when you are limited

When you call an LLM API, **you** meet rate limits (requests per minute and tokens per minute).

- On `429`, wait (`Retry-After` if given), then retry with **exponential backoff and jitter**.
- Keep a **concurrency limit**: at most, say, 10 LLM calls at a time, using a semaphore. Extra calls wait in line. This is called **backpressure** (chapter 11).
- Have a **fallback**: a second provider or a smaller model.

::: {.box .fastapi}
**How FastAPI does this**

- Add a limiter as a **dependency** or **middleware**. The `slowapi` library gives `@limiter.limit("10/minute")` and can use Redis for shared counters.
- Return `HTTPException(429)` and set the `Retry-After` header.
- For LLM calls inside your app, use `asyncio.Semaphore(10)` around the call.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Counting in server memory when you run more than one server.
- Limiting only by IP, so one office gets blocked together (or one attacker uses many IPs).
- No limit on `/login` and password reset.
- Returning `500` instead of `429`, or forgetting `Retry-After`.
- Clients that retry instantly in a loop after `429`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Explain the token bucket.**
Tokens refill at a steady rate up to a maximum. Each request spends a token. No tokens means rejection. It allows bursts while keeping the average rate fixed.

**Q: Fixed window vs sliding window?**
Fixed window resets at clock boundaries and can allow double the rate around the edge. Sliding window counts the last N seconds from now, so it is smoother but costs more.

**Q: How do you rate limit across many servers?**
Keep the counters in a shared store like Redis, using atomic commands (`INCR`, Lua scripts).

**Q: Which status code and headers?**
`429 Too Many Requests` with `Retry-After` and the `X-RateLimit-*` headers.

**Q: Design a rate limiter** (a common LLD question). Use a token bucket per key, stored in Redis, enforced in a gateway or middleware, with limits by plan.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. A fixed window allows 60 requests per minute. Show how a client can send 120 requests in 2 seconds.
2. A token bucket has size 5 and refills 1 token per second. A client sends 8 requests at second 0. How many pass? How many pass at second 3 if they send 3 more?
3. Choose the key for: (a) the login page, (b) a paid API with plans, (c) a free public search endpoint.
4. Your app has 4 servers, and each limits a user to 100 per minute in memory. What is the real limit and how do you fix it?
5. **Think:** why do LLM-based features need a limit even for logged-in users?
:::
