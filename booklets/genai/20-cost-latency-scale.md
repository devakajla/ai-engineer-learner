# 20. Cost, latency and scale

A demo works for one user. A product must work for thousands, quickly and within a budget. This chapter is about the three numbers that decide whether an LLM feature survives: **cost, latency and reliability under load.**

## Where the money goes

Chapter 2 gave the formula: `cost = input tokens x input price + output tokens x output price`. In RAG, most input tokens are **retrieved chunks and history**, not the question. That is where you save.

Levers, from the easiest:

| Lever | How |
| --- | --- |
| smaller model for easy tasks | routing (below) |
| shorter prompts | trim rules, fewer chunks, rerank to keep the best |
| shorter outputs | ask for brevity, set `max_completion_tokens` |
| cache repeated work | prompt caching, exact and semantic caches |
| batch offline jobs | batch APIs are cheaper, and slower |
| avoid calls | answer "I do not know" before calling when retrieval is empty |

## Latency: where the time goes

For a streaming chat, two numbers matter:

- **Time to first token (TTFT):** how long until the first word appears. Dominated by network, prompt size and queueing.
- **Tokens per second:** speed after that. Dominated by model size and the provider.

A RAG request adds up: embed the question, vector search, rerank, then the LLM. Measure **each step** (chapter 21). Typical wins: stream the answer, use a small fast model, cut the prompt, run independent steps in **parallel**, and cache.

## Exact cache

If the same question and settings come again, return the saved answer. A dictionary or Redis with a key made from the model, the settings and the messages is enough. It gives zero cost and near-zero latency. It only helps with repeated, identical requests.

## Semantic cache

Users ask the same thing in different words. A **semantic cache** embeds the question, and returns a saved answer when a past question is **close enough** (cosine above a threshold). We ran this with the toy embedder:

```python
class SemanticCache:
    def __init__(self, threshold=0.9):
        self.items = []                      # list of (vector, answer)
        self.threshold = threshold

    def get(self, question):
        vector = embed(question)
        for saved_vector, answer in self.items:
            if float(saved_vector @ vector) >= self.threshold:
                return answer
        return None

    def put(self, question, answer):
        self.items.append((embed(question), answer))

cache = SemanticCache()
cache.put("how to get my money back refund", "30 days")
print(cache.get("refund money back please"))
# -> 30 days
print(cache.get("reset password"))
# -> None
```

A reworded question hit the cache, and an unrelated one missed it. Care points: a **threshold too low** returns a wrong answer for a different question, and cached answers go **stale** when documents change (use an expiry, and clear on re-index). Never share a cache across users if answers depend on user data. A real version uses a vector index, not a loop.

## Model routing

Not every question needs the biggest model. A **router** sends easy questions to a small, cheap model, and hard ones to a large one. The router can be simple rules, or a tiny classifier call.

```python
def route(question):
    if len(question.split()) < 12 and "?" in question:
        return "small"
    return "large"

print(route("What is the refund window?"))
# -> small
```

Always measure with your evals (chapter 16): a cheaper route must keep quality. Also add a **fallback**: if the small model's answer fails a check, retry on the large one.

## Concurrency limits

A hundred users at once means a hundred simultaneous LLM calls, and a provider will answer `429` (chapter 5). Control it with a **semaphore** that caps parallel calls (Python booklet, chapter 15). We ran a cap of 2 over 6 tasks, and the peak number running at the same time was 2:

```python
import asyncio

semaphore = asyncio.Semaphore(2)

async def call_llm(question):
    async with semaphore:
        ...  # the real call goes here
```

Also: a **queue** for long jobs (a worker takes them), per-user **rate limits**, and **backpressure** (when too busy, say so quickly instead of piling up requests).

@@ flow | Figure 20.1: protecting the LLM provider and your wallet.
Requests|many users|blue -> Per-user limit|fair use;budget|yellow -> Queue and semaphore|cap parallel calls|purple -> LLM provider|stays under its limit|green
@@ end

## Batching

When work is not urgent (summarise 10,000 documents overnight), use **batch** endpoints if the provider has them. Also embed many texts per call (embedding APIs take lists), instead of one by one. Batching reduces overhead and often price.

## Scaling the retrieval side

- **Index size:** 100,000 vectors of 384 float32 numbers is about 154 MB. Two million vectors of 768 numbers is about 6 GB. Plan memory (chapter 12).
- **Read load:** replicas of the vector DB, or a managed service.
- **Ingestion:** a queue and workers, parse and embed in parallel, idempotent jobs (safe to run twice).
- **Updates:** per-document delete and re-insert, plus a plan for re-embedding on model change.

## Multi-tenant isolation

If many customers share one index, **every query must be filtered by tenant id**, in the database call. Options:

| Approach | Good | Careful |
| --- | --- | --- |
| one collection with a `tenant_id` filter | cheap, simple | one missed filter leaks data. Test it. |
| a collection per tenant | strong isolation | many collections, more cost |
| a separate database per tenant | strongest | highest cost, for regulated data |

Whatever you pick, add a **test** that user A can never retrieve user B's chunks, and keep tenant ids out of the model's control.

## A cost estimate to practise

```python
def monthly_cost(requests_per_day, in_tokens, out_tokens, in_price, out_price):
    per_request = in_tokens / 1e6 * in_price + out_tokens / 1e6 * out_price
    return per_request * requests_per_day * 30

print(round(monthly_cost(30_000, 1200, 300, 0.05, 0.08), 2))
# -> 75.6
```

The same numbers as chapter 2 (2.52 dollars a day) give **75.60 dollars a month**. Now shorten the prompt from 1200 to 800 tokens and compare. Doing such estimates **before** you build is a good engineering habit, and a common interview task.

::: {.box .checkpoint}
**Checkpoint:** you can name four ways to cut cost, explain TTFT, and describe how you keep tenants apart.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using the biggest model for everything.
- A semantic cache with a loose threshold.
- Caching answers across users who see different data.
- No limit on parallel calls, then constant 429 errors.
- A tenant filter that one code path forgets.
- Never estimating cost before launch.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you reduce LLM cost?** Smaller models through routing, shorter prompts and fewer chunks, output limits, caching (exact, semantic, prompt), batching, and skipping calls when retrieval is empty.

**Q: How do you reduce latency?** Stream, use faster models, shrink the prompt, run independent steps in parallel, cache, and measure each stage.

**Q: What is a semantic cache and its risk?** It reuses answers for similar questions using embedding similarity. Too loose a threshold gives wrong answers, and entries can go stale.

**Q: How do you handle many concurrent users?** Semaphores and queues, per-user rate limits, retries with backoff, and backpressure.

**Q: How do you isolate tenants in a vector DB?** Mandatory tenant filter in every query, or separate collections or databases, plus tests that prove no cross-tenant retrieval.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Compute the monthly cost for 100,000 requests a day with 2,000 input and 400 output tokens, at 0.05 and 0.08 dollars per million.
2. Add `max_entries` to `SemanticCache` that drops the oldest item.
3. Add an expiry time to cache entries, using a fake clock in the test.
4. Write a test that proves tenant A cannot see tenant B's chunks in a Chroma collection with `where={"tenant": ...}`.
5. Write a router that sends questions with the word "compare" to the large model.
6. **Think:** your cache hit rate is 40 percent. How much does that cut your bill, and what risk did you add?
:::
