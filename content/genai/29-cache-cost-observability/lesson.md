---
title: Caching, cost, rate limits and observability
summary: Make an LLM app cheaper, faster and safe to run - reuse answers with a cache, control the money, limit how often users can call, and log every call so you can see what happens.
plan_ids: []
---

A demo calls the model a few times. A real app calls it thousands of times a day, for many users, and every call costs money and time. Three things go wrong sooner or later:

1. **The bill surprises you.** One user (or one bug in a loop) runs up a big cost.
2. **The app is slow.** The same question is answered again and again.
3. **You cannot tell what happened.** A user says "the answer was wrong yesterday" and you have no record.

This lesson gives you four tools: **caching**, **cost control**, **rate limits** and **observability** (being able to see inside your running app).

## 1. Caching: do not pay twice for the same answer

A **cache** is a memory of answers you already have. Before you call the model, you look in the cache. If the answer is there, you return it at once: no cost, no wait. If not, you call the model, and store the answer for next time.

```
request -> [ cache has it? ] -- yes --> answer (free, instant)
                  |
                  no
                  v
              call the model -> store in cache -> answer
```

### The key

To find an answer again, you need a **key**: something that is equal for equal requests. The key must include **everything that changes the answer**: the model name, the messages, the temperature (and tools, if any). Forget one of these and you return a wrong answer.

A neat way: turn the request into text, then **hash** it (lesson 39) to get a short key.

Let's practise the pattern with a different example: a key for a pizza order. The key must be the same when the order dictionary is written in a different key order.

1. Put the order in a dictionary.
2. Turn it into text with `json.dumps(..., sort_keys=True)`, so the order of keys does not matter.
3. Hash the text and keep the first characters.

```python
import hashlib
import json

def order_key(order):
    text = json.dumps(order, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]

a = order_key({"size": "large", "topping": "corn"})
b = order_key({"topping": "corn", "size": "large"})
print(a == b)        # -> True
print(len(a))        # -> 8
```

The first exercise is the same, for model calls.

### Using the cache

The pattern: build the key, look in the dictionary, call only on a miss, store the result.

Let's practise it with a different example: a slow `square_slowly` function, and a dictionary as the cache.

1. Look in the cache first. If found, return it and say it was cached.
2. If not, do the slow work.
3. Store the result and return it.

```python
def cached_square(cache, number):
    if number in cache:
        return {"value": cache[number], "cached": True}
    value = number * number          # imagine this is slow
    cache[number] = value
    return {"value": value, "cached": False}

cache = {}
print(cached_square(cache, 7))   # -> {'value': 49, 'cached': False}
print(cached_square(cache, 7))   # -> {'value': 49, 'cached': True}
```

The cache is a plain dictionary that you **change in place**. In production you use a shared store such as **Redis**, so all your servers share the cache. The idea is the same.

### When NOT to cache

- **Temperature above 0.** The answers are *meant* to differ. A cached one defeats the purpose. Cache only at temperature 0 (or when you really want the same answer each time).
- **Personal or private prompts.** If the prompt holds one user's data, a shared cache can hand it to another user (lesson 40: the cache key must include the user's access scope).
- **Answers that go out of date** (today's weather, stock prices). Give cache entries a **TTL** (time to live): after, say, 10 minutes the entry is thrown away.
- **Tool-using agents** where results depend on the outside world.

### Two more caches to know

- **Prompt caching (provider side).** Many providers remember the start of a long prompt for a short time. If the next request has the same start (a long system prompt or a document), that part is cheaper and faster. You do nothing special except keep the **stable part first** and the changing part last. Check your provider's docs for the exact rules and prices.
- **Semantic cache.** It also catches questions that are *similar*, not equal ("how do I reset my password" and "password reset steps"). You embed the question and look for a close vector (lesson 14). It saves more, but it can return a wrong answer for a question that only *looks* similar. Use it with a strict similarity threshold, and only for low-risk questions like FAQs.

## 2. Cost control

Cost per call = (input tokens x input price) + (output tokens x output price), prices are per million tokens (lesson 35). Ways to keep the bill under control:

| Lever | How |
| --- | --- |
| **Shorter prompts** | Fewer chunks (lesson 24), shorter system prompt, trim old chat history (lesson 12) |
| **`max_completion_tokens`** | Always set it. It is a hard cap on the output cost |
| **A smaller model for easy jobs** | **Routing**: a cheap, fast model for simple tasks (classify, extract), a strong one for hard ones |
| **Cache** | See above |
| **Batching** | Embedding calls in batches (lesson 39). Some providers have a cheaper batch API for jobs that can wait |
| **Stop early** | Agent `max_steps` and a token budget (lesson 27) |
| **Budgets and alerts** | A daily limit per user and for the whole app, and an alert when it is passed |

Two numbers worth tracking: **cost per request** and **cost per user per day**. If you know them, a price change or a bug shows up the same day.

Important: output tokens are usually more expensive than input tokens, and **thinking tokens** (lesson 34) count as output. A "reasoning" model can cost several times more for the same question.

## 3. Rate limits

There are two different limits, and people mix them up:

- **The provider's limit on you.** Groq returns HTTP `429` when you send too many requests or tokens. You handle it with retries and backoff (lesson 6).
- **Your limit on your users.** You decide how often each user may call **your** app. This protects your budget and your servers from one heavy user, a bug, or an attack.

The simplest design is a **sliding window**: for each user, keep the times of their recent requests. A new request is allowed if there are fewer than `limit` requests in the last `window` seconds.

Let's practise the idea with a different example: a door that lets in at most 2 people every 10 seconds. We keep the arrival times.

1. Keep only the times that are still inside the window.
2. If there is room, let the person in and remember the time.
3. If not, say how long to wait: until the oldest time leaves the window.

```python
def let_in(times, now, limit=2, window=10):
    recent = [t for t in times if now - window < t <= now]
    if len(recent) < limit:
        return {"ok": True, "times": recent + [now], "wait": 0}
    return {"ok": False, "times": recent, "wait": recent[0] + window - now}

state = let_in([], 0)
state = let_in(state["times"], 3)
print(let_in(state["times"], 5))    # -> {'ok': False, 'times': [0, 3], 'wait': 5}
print(let_in(state["times"], 11))   # -> {'ok': True, 'times': [3, 11], 'wait': 0}
```

At time 5 the window is `(-5, 5]`, and both earlier people are inside, so the door is closed. The oldest one (time 0) leaves the window at time 10, so the wait is `0 + 10 - 5 = 5`. At time 11 the person from time 0 is gone, so there is room. The third exercise is this logic.

What to do when you block a request:
- Return HTTP **429** with a `Retry-After` header (the wait in seconds).
- Do **not** call the model for a blocked request.
- Choose limits for **requests** *and* for **tokens or money** (a few huge requests can cost more than many small ones).

Other designs you will meet: **fixed window** (count per minute, simple but allows bursts at the edges), **token bucket** (a bucket refills at a steady speed, each request takes a token, allows short bursts). In production the counters live in a shared store like Redis, so all servers see the same numbers.

## 4. Observability: see what your app does

**Observability** means you can answer "what happened?" about any request, after the fact. LLM apps need it more than normal apps, because the output differs every time and failures are quiet (a wrong answer is not an error).

### What to log for every model call

- A **request id** (to connect all logs of one user request).
- The user or tenant id (not the private content, if you can avoid it).
- The **model** and the **prompt version** (lesson 8).
- **Tokens** in and out, and the **cost**.
- **Latency**: the time to the first token and the total time.
- The **status**: ok, error type, retries, timeouts, `finish_reason` (lesson 5: `length` means the answer was cut).
- For RAG: the question, the retrieved chunk ids and scores (lesson 24). For agents: every step and tool call with its result (lesson 27).
- User **feedback** (thumbs up or down), linked to the request id.

Store prompts and answers only if your privacy rules allow it. Mask personal data first (lesson 30), and set a retention time.

### What to compute from the logs

- **Error rate** and which errors.
- **Cost** per day, per user, per feature.
- **Latency percentiles.** The **average** hides the slow ones. The **p95** is the time that 95% of calls beat. If the average is 1.2 seconds and p95 is 9 seconds, one user in twenty is having a bad time.
- **Cache hit rate** (how many requests were answered from the cache).
- **Quality** numbers from your evaluation (lessons 25 and 41), run on a sample of real traffic.

Let's practise the "summarize a log" pattern with a different example: summarize the delivery times of a pizza shop. For each order we have minutes and whether it arrived hot.

1. Loop over the orders. Collect the minutes and count the cold ones.
2. Sort the minutes. The 95th percentile is the item at index `ceil(0.95 * n) - 1`.
3. Guard the case of no orders first.

```python
import math

def summarize_orders(orders):
    n = len(orders)
    if n == 0:
        return {"n": 0, "cold_rate": 0.0, "avg": 0.0, "p95": 0}
    minutes = []
    cold = 0
    for order in orders:
        minutes.append(order["minutes"])
        if not order["hot"]:
            cold += 1
    minutes.sort()
    return {
        "n": n,
        "cold_rate": round(cold / n, 4),
        "avg": round(sum(minutes) / n, 1),
        "p95": minutes[math.ceil(0.95 * n) - 1],
    }

orders = [{"minutes": 20, "hot": True}, {"minutes": 45, "hot": False}, {"minutes": 25, "hot": True}]
print(summarize_orders(orders))   # -> {'n': 3, 'cold_rate': 0.3333, 'avg': 30.0, 'p95': 45}
```

The last exercise builds the same kind of report for model calls, with cost added.

### Tracing

For an agent or a RAG pipeline, one user request makes many steps. A **trace** is the tree of all steps of one request, with times and values. Tools such as **Langfuse**, **LangSmith** and **OpenTelemetry**-based services record and show traces, and let you search them. They change quickly, so check their docs. They are worth using from the first week of a real app, because a trace is the only way to see why one answer went wrong.

## Try it live

1. Wrap your Groq call in `cached_call` (from the exercise). Ask the same question twice at temperature 0. Time both. The second should take almost 0 ms.
2. Write a `log_call` function that appends a dictionary (model, input tokens, output tokens, ms, ok) to a list after every call. Run 10 questions. Then call your `summarize_calls` on the list.
3. Add a rate limit of 3 calls per 20 seconds in front of the model. Fire 5 requests quickly. Which are blocked, and what is the `retry_after`?
4. Set `max_completion_tokens=30` and look at `finish_reason`. Count how often answers are cut.
5. Compute the cost of 1000 calls like yours, using the real prices on `console.groq.com`.

## A little deeper

- **Cache stampede.** When a popular cache entry expires, many requests may miss at the same moment and all call the model. Fixes: a lock so only one recomputes, or refresh the entry slightly before it expires.
- **Idempotency.** If a client retries a request after a timeout, you may pay twice. An **idempotency key** (a unique id per request) lets the server return the first result instead of running again.
- **Budgets per tenant.** Count tokens and cost per tenant. Block or slow a tenant that passes its budget, and tell them, instead of surprising yourself at the end of the month.
- **Retries cost money.** Each retry is a new paid call. Cap the number of tries, and do not retry errors that cannot succeed (a bad request, a missing key).
- **Percentiles need enough data.** A p95 over 10 calls is almost the maximum. Use real volume, or say how few calls you have.
- **Sampling.** Logging every full trace can be heavy. Keep all errors and slow calls, and a sample of the normal ones.
- **Alerts.** Alert on symptoms users feel (error rate, p95, cost per hour), not on every small thing, or people stop reading them.
- **Privacy.** Logs are data too. Mask personal data, limit who can read them, and delete them on schedule (lesson 40).

## Common mistakes

- A cache key that misses something that changes the answer (the model, the temperature, a system prompt version).
- Caching at temperature above 0, or caching one user's private answer for everyone.
- No TTL, so stale answers live forever.
- Not setting `max_completion_tokens`.
- Rate limiting only by requests, and ignoring tokens and money.
- Calling the model for a request you are about to block.
- Looking only at the average latency.
- Logging everything, including secrets and personal data, with no retention rule.
- No request id, so you cannot connect the logs of one request.
- Finding out about a cost problem from the invoice.

## Interview corner

**How do you reduce the cost of an LLM app?**
Shorter prompts and less context, a hard cap on output tokens, a cheaper model for easy tasks (routing), caching (exact, provider prompt caching, and carefully a semantic cache), batching, step and budget limits for agents, and budgets and alerts per user.

**What can you cache, and what should you not cache?**
Cache deterministic requests (temperature 0) with a key made from the model, messages and settings. Do not cache random outputs, private data across users, or fast-changing facts without a TTL.

**How do you rate limit an LLM API?**
A per-user sliding window or token bucket, counted in a shared store, on both requests and tokens or cost. Return 429 with `Retry-After` and do not call the model for blocked requests. Separately, handle the provider's 429 with backoff.

**What do you monitor in production?**
Error rate, latency percentiles (p50, p95), tokens and cost per request and per user, cache hit rate, `finish_reason` of `length`, and quality scores from sampled evaluations. Plus traces for agents and RAG.

**Why p95 and not just the average?**
The average hides the slow tail. p95 shows what the slowest 5% of users feel.

## Summary

- Cache: look before you call. The key covers model, messages and temperature. Cache only deterministic calls, never private data across users, and use a TTL for changing facts.
- Provider prompt caching rewards a stable prompt start. A semantic cache saves more but needs a strict threshold.
- Control cost: shorter prompts, `max_completion_tokens`, routing to a cheaper model, batching, agent limits, budgets and alerts.
- Two rate limits: the provider's limit on you (429, backoff) and your limit on users (sliding window or token bucket, on requests and tokens, `429` plus `Retry-After`).
- Observability: log request id, model, prompt version, tokens, cost, latency, status and feedback. Compute error rate, cost, p50 and p95, and cache hit rate.
- Use traces for agents and RAG (Langfuse, LangSmith, OpenTelemetry).
- Protect logs: mask personal data and set retention.
- Reference: `reference/genai-groq.md`.
