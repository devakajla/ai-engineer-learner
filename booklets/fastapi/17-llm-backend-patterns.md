# 17. LLM backend patterns

An AI Engineer builds backends that call language models. These calls are different from a normal database call: they are **slow** (seconds), **expensive** (you pay per token), **flaky** (rate limits, timeouts) and their output is **text that may be wrong**. This chapter turns those facts into patterns.

(The GenAI booklet teaches the models themselves. Here we only care about the backend side.)

## Idea: treat the LLM like any unreliable remote service

@@ flow | Figure 17.1: what surrounds one LLM call in a backend.
Check input|length, auth, rate limit|blue -> Build prompt|template + the user text|yellow -> Call the model|timeout, retry, stream|red -> Check output|parse, validate, limit|green
@@ end

## Pattern 1: always set a timeout and a token limit

```python
response = await client.chat.completions.create(
    model=settings.groq_model,
    messages=messages,
    max_completion_tokens=300,   # cost and length cap
    timeout=30,                  # seconds
)
text = response.choices[0].message.content
```

No timeout: a stuck call holds your request, a worker and your user, forever. No token cap: one request can produce a huge bill.

## Pattern 2: retry with backoff, but only for the right errors

Retry **temporary** errors (rate limit `429`, server `5xx`, timeout). Do not retry **your** mistakes (`400`, `401`, `422`). Wait longer each time, with a little randomness (**jitter**) so many clients do not retry at the same instant.

```python
import asyncio
import random


async def call_with_retry(make_call, tries: int = 3):
    for attempt in range(1, tries + 1):
        try:
            return await make_call()
        except (TimeoutError, ConnectionError):
            if attempt == tries:
                raise
            wait = (2 ** attempt) * 0.5 + random.random() * 0.2
            await asyncio.sleep(wait)
```

Real SDKs (`groq`, `openai`) already retry a few times by default. Know what yours does before adding your own.

## Pattern 3: structured output you can trust

If your code needs data (not prose), ask for JSON and **validate it with Pydantic**. Never trust the text.

```python
from pydantic import BaseModel, ValidationError


class TaskIdea(BaseModel):
    title: str
    priority: int


async def extract_task(client, text: str) -> TaskIdea:
    messages = [
        {"role": "system", "content": 'Reply with JSON only: {"title": str, "priority": 1-3}'},
        {"role": "user", "content": text},
    ]
    for attempt in range(2):                       # one retry on bad output
        reply = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            response_format={"type": "json_object"},
            max_completion_tokens=100,
        )
        raw = reply.choices[0].message.content
        try:
            return TaskIdea.model_validate_json(raw)
        except ValidationError as error:
            # tell the model what was wrong and try once more
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"Invalid: {error.errors()[0]['msg']}. Return valid JSON only."},
            ]
    raise ValueError("model did not return valid JSON")
```

With a fake client that first returns bad JSON and then good JSON, this returned `title='Buy milk' priority=2`. The loop is **parse, validate, feed the error back, retry**. The GenAI booklet shows schema-constrained output, which makes this even safer.

## Pattern 4: stream for the user, count for you

For chat, stream tokens (chapter 13). For your own cost tracking, log the **usage** the API returns:

```python
usage = response.usage                      # prompt_tokens, completion_tokens, total_tokens
logger.info("llm model=%s in=%s out=%s user=%s",
            model, usage.prompt_tokens, usage.completion_tokens, user.id)
```

Cost is roughly `input_tokens * input_price + output_tokens * output_price`. Prices differ per model, so keep them in settings.

## Pattern 5: limit who can spend your money

Every LLM route needs:

1. **Login** (chapter 11), so you know who is calling.
2. A **per-user rate limit** (for example 10 requests per minute).
3. A **daily token or request budget** per user.
4. A **maximum input length** (`Query(max_length=500)`).

A simple per-user limit with Redis (a fixed window counter):

```python
async def check_rate_limit(redis, user_id: int, limit: int = 10, window: int = 60) -> None:
    key = f"rl:{user_id}:{int(time.time()) // window}"
    count = await redis.incr(key)           # add 1, atomically
    if count == 1:
        await redis.expire(key, window)     # the counter disappears after the window
    if count > limit:
        raise HTTPException(429, "Too many requests", headers={"Retry-After": str(window)})
```

Call it at the start of the route. `INCR` is atomic, so two requests at the same instant are counted correctly. The Backend booklet (chapter 10) explains token buckets and sliding windows for more exact limits.

## Pattern 6: cache repeated answers

If many users ask the same thing, do not pay twice. Key a Redis entry by a hash of the prompt (and model) with a time limit:

```python
import hashlib, json

key = "llm:" + hashlib.sha256(f"{model}|{prompt}".encode()).hexdigest()
cached = await redis.get(key)
if cached:
    return json.loads(cached)
answer = await call_model(prompt)
await redis.set(key, json.dumps(answer), ex=3600)     # keep for 1 hour
```

Cache only answers that do not depend on the user, and only when the temperature is low (the answer is the same each time).

## Pattern 7: long jobs go to the queue

Summarising 200 pages takes a minute. Do not hold an HTTP request open. Use chapter 12: enqueue, return `202` and a job id, and let the worker call the model. The user polls or gets a stream.

## Pattern 8: concurrency limits

If a page needs 20 LLM calls, `gather` them with a **semaphore** (chapter 9) so you do not hit the provider's rate limit:

```python
sem = asyncio.Semaphore(5)

async def one(prompt):
    async with sem:
        return await call_model(prompt)

answers = await asyncio.gather(*(one(p) for p in prompts))
```

## Pattern 9: fallbacks

When the main model is down or too slow, try a second model (or provider) and degrade gracefully:

```python
for model in ("llama-3.1-8b-instant", "backup-model-name"):
    try:
        return await call_model(model, prompt)
    except Exception:
        logger.warning("model %s failed", model)
raise HTTPException(503, "AI service is busy, try again")
```

(Model names change; look up current ones in the provider's docs.)

## Pattern 10: safety at the edge

- The user's text goes into a prompt. A hostile user can write "ignore your instructions...". This is **prompt injection**. Keep the system prompt separate from user text, never put secrets in prompts, and never let model output run commands or SQL directly.
- Do not log full prompts if they may contain private data.
- Validate the output before using it (Pattern 3).

## Embeddings and search (a preview)

Many AI features need **embeddings**: a list of numbers that represents the meaning of a text. Similar texts have nearby vectors. A backend stores them (in `pgvector` or Chroma) and finds the nearest ones for a question. That is the base of RAG. The GenAI booklet builds it step by step. In FastAPI terms: an `EmbeddingService` and a `VectorRepository`, injected like any other dependency.

## Where it goes in TaskFlow

```
app/services/llm_service.py     # stream_answer, extract_task (no HTTP inside)
app/api/routes/chat.py          # login, rate limit, then call the service
app/core/rate_limit.py          # check_rate_limit (uses Redis)
```

The service takes `client` as an argument, so tests use a fake (chapter 15).

::: {.box .checkpoint}
**Checkpoint:** you can name, for any LLM route you write, its timeout, token cap, retry rule, rate limit, and what happens when the model is down.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- No timeout and no `max_completion_tokens`.
- Retrying every error, including `400` and `401`.
- Trusting model output as valid JSON without validation.
- Leaving the LLM route open to anonymous users.
- Putting the API key in code or in git.
- Logging private user prompts.
- Calling the model inside a loop one by one instead of in a controlled concurrent batch.
- Mixing HTTP code and model code in one function, which makes tests hard.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you make an LLM call reliable in a backend?**
Timeout, token cap, retries with backoff for temporary errors only, a fallback model, and a clear error for the user when all fail.

**Q: How do you get structured data from an LLM?**
Ask for JSON (or use schema-constrained output), validate with Pydantic, and on failure send the error back to the model for a limited number of retries.

**Q: How do you control cost?**
Token caps, per-user rate limits and budgets, caching repeated prompts, a cheaper model for easy tasks, and logging usage per user.

**Q: What is prompt injection?**
User or document text that tries to override your instructions. Reduce the risk by separating system and user content, limiting what the model can do, and validating outputs.

**Q: Why stream LLM responses?**
The first words show up in about a second instead of waiting for the whole answer, which feels much faster.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write a fake client that raises `TimeoutError` twice and then succeeds, and test `call_with_retry` with it (patch `asyncio.sleep` or use a short wait).
2. Add the rate limit to `/chat/stream` and test it with a fake Redis class that has `incr` and `expire`.
3. Write `extract_task` tests with a fake client that returns bad JSON first and good JSON second.
4. Add a usage log line to the chat route and compute the cost of a 500 input + 200 output token call at made-up prices.
5. **Think:** which LLM routes in an app should never be public, and why?
:::
