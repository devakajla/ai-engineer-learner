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
