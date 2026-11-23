# Step 25 — Cache, rate limit and cost

The server from step 24 works, but every question costs a model call, one user can send a thousand requests, and you cannot see what anything costs. This step (lesson 29) adds three protections: a **cache**, a **rate limit**, and **call records with a cost summary**.

Your folder after this step (new files marked):

```
devdocs-copilot/
└── copilot/
    ├── cache.py     <- new
    ├── server.py    <- changed: cache, rate limit, /stats
    └── ... (all files from step 24)
```

### 1. `copilot/cache.py`

```python
"""Cache, rate limit and cost: save money, protect the service, and see what it costs."""

import hashlib
import json
import math
import time

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import NO_ANSWER, build_rag_messages, retrieve

# Made-up example prices in dollars per 1 million tokens: (input, output).
# Look up the real prices of your model on console.groq.com before you trust any cost number.
EXAMPLE_PRICES = {DEFAULT_MODEL: (0.30, 0.60)}


def cache_key(model, messages, temperature):
    """The same model, messages and temperature give the same key. Key order in dicts does not matter."""
    payload = json.dumps({"model": model, "messages": messages, "temperature": temperature}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def cached_call(cache, client, messages, model=DEFAULT_MODEL, temperature=0, calls=None, clock=time.perf_counter):
    """Call the model, or return the saved answer. Only temperature 0 is cached (other answers should vary).

    When calls is a list, every REAL call adds a record: {"model", "input", "output", "ms", "ok"}.
    Returns {"text", "cached"}.
    """
    key = cache_key(model, messages, temperature)
    if temperature == 0 and key in cache:
        return {"text": cache[key], "cached": True}
    start = clock()
    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    except Exception:
        if calls is not None:
            calls.append({"model": model, "input": 0, "output": 0, "ms": round((clock() - start) * 1000), "ok": False})
        raise
    text = response.choices[0].message.content
    if calls is not None:
        usage = getattr(response, "usage", None)
        calls.append({
            "model": model,
            "input": getattr(usage, "prompt_tokens", 0) or 0,
            "output": getattr(usage, "completion_tokens", 0) or 0,
            "ms": round((clock() - start) * 1000),
            "ok": True,
        })
    if temperature == 0:
        cache[key] = text
    return {"text": text, "cached": False}


def cached_rag_answer(cache, client, collection, question, k=3, embed=embed_texts, model=DEFAULT_MODEL, calls=None):
    """RAG with a cache. The search always runs, and the key includes the chunks.

    So when the docs change, the prompt changes, the key changes, and nobody gets a stale answer.
    Returns {"answer", "hits", "cached"}.
    """
    hits = retrieve(collection, question, k=k, embed=embed)
    if not hits:
        return {"answer": NO_ANSWER, "hits": [], "cached": False}
    messages = build_rag_messages(question, hits)
    result = cached_call(cache, client, messages, model=model, temperature=0, calls=calls)
    return {"answer": result["text"], "hits": hits, "cached": result["cached"]}


def allow_request(timestamps, now, limit, window):
    """A sliding-window rate limit. timestamps are the times of the accepted requests (seconds).

    Returns {"allowed", "timestamps", "retry_after"}. The input list is not changed.
    """
    recent = [t for t in timestamps if now - window < t <= now]
    if len(recent) < limit:
        return {"allowed": True, "timestamps": recent + [now], "retry_after": 0}
    return {"allowed": False, "timestamps": recent, "retry_after": recent[0] + window - now}


def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    """Dollars for one call. Prices are per 1 million tokens."""
    return round(input_tokens / 1_000_000 * input_price + output_tokens / 1_000_000 * output_price, 6)


def summarize_calls(calls, prices):
    """One summary of many call records: errors, cost, average and p95 time. A model without a price counts as unpriced."""
    n = len(calls)
    if n == 0:
        return {"n": 0, "errors": 0, "error_rate": 0.0, "total_cost": 0.0, "avg_ms": 0.0, "p95_ms": 0, "unpriced": 0}
    errors = 0
    total_cost = 0.0
    unpriced = 0
    times = []
    for call in calls:
        times.append(call["ms"])
        if not call["ok"]:
            errors += 1
        if call["model"] in prices:
            input_price, output_price = prices[call["model"]]
            total_cost += estimate_cost(call["input"], call["output"], input_price, output_price)
        else:
            unpriced += 1
    times.sort()
    return {
        "n": n,
        "errors": errors,
        "error_rate": round(errors / n, 4),
        "total_cost": round(total_cost, 6),
        "avg_ms": round(sum(times) / n, 1),
        "p95_ms": times[math.ceil(0.95 * n) - 1],
        "unpriced": unpriced,
    }
```

Read it in parts:

1. **`cache_key`** turns the model, the messages and the temperature into a short fixed text (a hash). Same input, same key. `sort_keys=True` makes the key the same when the dict keys come in another order. Anything that changes the answer must be **in the key**.
2. **`cached_call`** returns the saved text for a known key. It caches **only temperature 0**. At a higher temperature the user wants variety, so a saved answer would be wrong. Every **real** call (cache miss) adds a record with the tokens (from `usage`), the time and `ok`. A failed call is recorded with `ok: False` and then raised again. A cache hit is not a call and costs nothing, so it adds no record.
3. **`cached_rag_answer`** is the clever part. The search **always runs**, and the key is built from the **prompt**, which holds the chunks. If someone edits the docs, the chunks change, the key changes, and the old answer is not used. A cache keyed only on the question would serve **stale** answers.
4. **`allow_request`** is a **sliding window** limiter. It keeps the times of the accepted requests, drops the ones older than the window, and allows a new one only if fewer than `limit` remain. When it blocks, it says how many seconds until the oldest request leaves the window (`retry_after`). It returns a new list and does not change the old one.
5. **`estimate_cost`** is tokens divided by one million times the price per million, for the input and the output. `EXAMPLE_PRICES` holds **made-up numbers**. Real prices change. Look them up on the provider's pricing page.
6. **`summarize_calls`** gives the numbers you watch: count, errors, error rate, total cost, average time and **p95** time. A call whose model has no price counts as `unpriced` instead of silently costing zero.

### 2. Changes in `copilot/server.py`

Replace `create_app` and fix the imports at the top. The new parts, in short:

- `rate_limit` is a **dependency**. FastAPI runs it before the endpoint. It looks up the client address, calls `allow_request`, and raises **`429`** with a `Retry-After` header when blocked. `/health` has no limit, so monitoring never gets blocked.
- `/ask` uses `cached_rag_answer` and returns `"cached": true` or `false`.
- `/stats` returns `summarize_calls(...)`: how many real calls, errors, cost and p95.
- `limit`, `window` and `clock` are arguments of `create_app`, so a test can use a fake clock and a limit of 2.

```python
"""Serve Copilot over HTTP: a JSON endpoint, and a streaming endpoint that uses server-sent events (SSE)."""

import json
import math
import time

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from copilot.cache import EXAMPLE_PRICES, allow_request, cached_rag_answer, summarize_calls
from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import NO_ANSWER, build_rag_messages, retrieve


def format_sse(data, event=None):
    """One SSE message. Each line of data gets its own "data:" prefix. A blank line ends the message."""
    parts = []
    if event:
        parts.append("event: " + event)
    for line in data.split("\n"):
        parts.append("data: " + line)
    return "\n".join(parts) + "\n\n"


def chunk_text(chunk):
    """The new text in one stream chunk. Keep-alive chunks (no choices, or None content) give ""."""
    if not chunk.choices:
        return ""
    text = chunk.choices[0].delta.content
    return text or ""


def sse_stream(chunks):
    """Turn model chunks into SSE messages. A failure in the middle becomes an `error` event.

    Always ends with exactly one `done` or one `error` event, so the browser knows the stream is over.
    """
    try:
        for chunk in chunks:
            text = chunk_text(chunk)
            if text:
                yield format_sse(text, "token")
    except Exception as error:
        yield format_sse("stream failed: " + str(error), "error")
        return
    yield format_sse("[DONE]", "done")


def ask_events(client, collection, question, k=3, embed=embed_texts, model=DEFAULT_MODEL):
    """All SSE messages for one question: the sources first, then the answer text piece by piece."""
    try:
        hits = retrieve(collection, question, k=k, embed=embed)
    except Exception as error:
        yield format_sse("search failed: " + str(error), "error")
        return
    yield format_sse(json.dumps([hit["id"] for hit in hits]), "sources")
    if not hits:
        yield format_sse(NO_ANSWER, "token")
        yield format_sse("[DONE]", "done")
        return
    try:
        chunks = client.chat.completions.create(
            model=model, messages=build_rag_messages(question, hits), temperature=0, stream=True
        )
    except Exception as error:
        yield format_sse("stream failed: " + str(error), "error")
        return
    yield from sse_stream(chunks)


def create_app(client, collection, embed=embed_texts, model=DEFAULT_MODEL, limit=20, window=60.0, clock=time.time):
    """Build the app. Everything it needs lives on app.state, so tests can pass fakes.

    limit requests per window seconds are allowed for each client address.
    """
    app = FastAPI(title="DevDocs Copilot")
    app.state.client = client
    app.state.collection = collection
    app.state.embed = embed
    app.state.model = model
    app.state.limit = limit
    app.state.window = window
    app.state.clock = clock
    app.state.seen = {}  # client address -> times of accepted requests
    app.state.cache = {}  # saved answers
    app.state.calls = []  # one record per real model call

    def rate_limit(request: Request):
        state = request.app.state
        who = request.client.host if request.client else "unknown"
        verdict = allow_request(state.seen.get(who, []), state.clock(), state.limit, state.window)
        state.seen[who] = verdict["timestamps"]
        if not verdict["allowed"]:
            wait = str(math.ceil(verdict["retry_after"]))
            raise HTTPException(status_code=429, detail="too many requests", headers={"Retry-After": wait})

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ask", dependencies=[Depends(rate_limit)])
    def ask(request: Request, question: str = Query(min_length=1, max_length=2000)):
        state = request.app.state
        result = cached_rag_answer(
            state.cache, state.client, state.collection, question,
            embed=state.embed, model=state.model, calls=state.calls,
        )
        return {"answer": result["answer"], "sources": [hit["id"] for hit in result["hits"]], "cached": result["cached"]}

    @app.get("/stream", dependencies=[Depends(rate_limit)])
    def stream(request: Request, question: str = Query(min_length=1, max_length=2000)):
        state = request.app.state
        events = ask_events(state.client, state.collection, question, embed=state.embed, model=state.model)
        return StreamingResponse(
            events,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.get("/stats")
    def stats(request: Request):
        return summarize_calls(request.app.state.calls, EXAMPLE_PRICES)

    return app


def build_default_app():
    """For uvicorn --factory: the real client and the real index."""
    from copilot.llm import get_client
    from copilot.store import open_collection

    return create_app(get_client(), open_collection(".chroma"))
```

> The cache and the rate-limit table live in the memory of **one** process. With several workers each has its own copy. For production move both to Redis (lesson 29, "A little deeper").

### 3. Run it

```
uv run uvicorn copilot.server:build_default_app --factory --port 8100
curl "http://localhost:8100/ask?question=how%20do%20I%20delete%20a%20task"
curl "http://localhost:8100/ask?question=how%20do%20I%20delete%20a%20task"   # "cached": true
curl "http://localhost:8100/stats"
```

### Checkpoint

Run the tests. Then ask the same question twice and check that only one real call is counted in `/stats`. Send 25 requests in a loop and find the first `429`. Put the real prices of your model in `EXAMPLE_PRICES` (rename it if you like) and write down what 1,000 questions would cost.
