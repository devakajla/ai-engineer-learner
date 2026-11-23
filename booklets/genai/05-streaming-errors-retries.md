# 5. Streaming, errors, rate limits and retries

A call to an LLM is slow (seconds), it can fail, and providers limit how fast you may call. A beginner's code works on a good day. A good engineer's code works on a **bad** day too. This chapter is about that.

## Streaming: show the first word early

A model writes one token at a time. If you wait for the whole answer, a 20-second answer means 20 seconds of blank screen. With **streaming**, the server sends each piece as soon as it is ready, so the first words appear in under a second. The total time is the same, but it **feels** much faster.

```python
stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Tell a very short story."}],
    max_completion_tokens=200,
    stream=True,
)

for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)
```

What changes with `stream=True`:

- The call returns an **iterator** of chunks, not one response (chapter 10 of the Python booklet explains iterators).
- Each chunk has a small `delta`, a piece of the answer. `delta.content` can be `None` (for example in the first or last chunk), so check it.
- `end=""` and `flush=True` print the pieces on one line, right away.

To keep the full text as well, join the pieces:

```python
parts = []
for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        parts.append(piece)
        print(piece, end="", flush=True)
full_text = "".join(parts)
```

In a web backend, you pass these pieces to the browser using SSE (the FastAPI booklet, chapter 13). If the user closes the page, stop iterating, so you stop paying.

@@ flow | Figure 5.1: one request, many small pieces.
Request|stream=True|blue -> piece 1|"Once"|green -> piece 2|" upon"|green -> piece 3|" a time"|green -> done|finish_reason|gray
@@ end

## Why calls fail

| Error (Groq SDK name) | HTTP | Meaning | Retry? |
| --- | --- | --- | --- |
| `BadRequestError` | 400 | your request is wrong (bad parameter, too long) | **no**, fix it |
| `AuthenticationError` | 401 | bad or missing key | **no** |
| `PermissionDeniedError` | 403 | not allowed | **no** |
| `NotFoundError` | 404 | wrong model name | **no** |
| `RateLimitError` | 429 | you are calling too fast | **yes**, after waiting |
| `InternalServerError` | 5xx | the provider has a problem | **yes** |
| `APITimeoutError` | none | no answer in time | **yes** |
| `APIConnectionError` | none | network problem | **yes** |

The rule is simple. Errors that say **"you made a mistake"** (4xx, except 429) will fail again, so retrying wastes time. Errors that say **"try again later"** (429, 5xx, timeouts, connection) are **temporary**, so retry.

## Rate limits

Providers cap how much you can use, usually as **requests per minute** and **tokens per minute** (and sometimes per day). Go over, and you get `429`, often with a `retry-after` header that says how long to wait. Free tiers are tight.

Ways to stay inside: add a **semaphore** to cap parallel calls (Python booklet, chapter 15), count tokens before sending, spread work in time, and retry politely.

## Timeouts

Always set one. Without it, a stuck connection holds your program forever.

```python
client = Groq(timeout=30.0, max_retries=2)
```

The SDK already retries a couple of times by default (`max_retries`). Know your SDK's default before you add your own retry on top, or you will retry too many times (retries multiplied).

## Retry with exponential backoff and jitter

If a server is overloaded and 1,000 clients retry instantly, they overload it again. The polite way is **exponential backoff**: wait a little, then twice as long, then twice again. Add **jitter** (a small random amount) so clients do not all come back at the same moment.

```python
import random, time
import groq

RETRYABLE = (
    groq.RateLimitError,
    groq.APIConnectionError,
    groq.APITimeoutError,
    groq.InternalServerError,
)

def call_with_retry(fn, tries=4, base=0.5, sleep=time.sleep):
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except RETRYABLE:
            if attempt == tries:
                raise
            wait = base * 2 ** (attempt - 1) + random.random() * 0.1
            sleep(wait)
```

Walk through it. `fn` is any function that makes the call. We try up to 4 times. On a **retryable** error we wait `0.5`, then `1.0`, then `2.0` seconds (plus a little jitter). On the last try, we `raise`, so the caller still learns about the failure. A `BadRequestError` is not in `RETRYABLE`, so it passes straight up with no retry.

We pass `sleep` as an argument for one reason: **tests**. A test passes a fake `sleep` that records the waits and does not really wait.

A test with a fake that fails twice and then works (this was run):

```python
class Flaky:
    def __init__(self, errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"

waits = []
flaky = Flaky([rate_limit_error, connection_error])
print(call_with_retry(flaky, sleep=waits.append), flaky.calls, [round(w, 1) for w in waits])
# -> ok 3 [0.5, 1.0]
```

It succeeded on the third try, after waits of 0.5 and 1.0. (In a real test, build the SDK errors by hand, as the project's tests do, and check that a `BadRequestError` is tried **once**.)

In a call: `call_with_retry(lambda: client.chat.completions.create(...))`. The `lambda` wraps the call so it can be repeated.

## Fallback: a second option

When retries fail, do not just crash. Try another model (or another provider), and if everything fails, return a clear message.

```python
MODELS = ["llama-3.1-8b-instant", "a-backup-model-name"]

def ask_with_fallback(client, messages):
    last_error = None
    for model in MODELS:
        try:
            return call_with_retry(
                lambda: client.chat.completions.create(model=model, messages=messages)
            )
        except (groq.RateLimitError, groq.InternalServerError, groq.APIConnectionError) as error:
            last_error = error
    raise last_error
```

(Model names change. Put them in settings, not in code. Also remember the lambda uses `model` from the loop; this works here because the call runs right away, inside the same loop turn.)

Good systems also **degrade gracefully**: a smaller model, a cached answer, or "the AI helper is busy, try again in a minute".

## What to log on every call

Make debugging possible later: the model, the number of input and output tokens, the time it took, the `finish_reason`, the retry count, and a request id. Do not log the private text of users by default.

::: {.box .checkpoint}
**Checkpoint:** you can list which errors to retry and which not, explain backoff and jitter, and say why `sleep` is a parameter.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Retrying a `400` or `401`, which can never succeed.
- Retrying instantly in a tight loop (it makes overload worse).
- No timeout, so one call hangs for ever.
- Stacking your own retries on top of the SDK's without knowing the total.
- Streaming but printing the chunk without checking for `None`.
- Letting a generic `except Exception` hide a real bug as a "temporary" error.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Why stream LLM responses?** To show output as it is generated, so the first token arrives quickly and the app feels responsive.

**Q: How do you handle a 429?** Wait (respecting `retry-after` if given), retry with exponential backoff and jitter, and reduce the request rate or concurrency.

**Q: Which errors should not be retried?** Client errors such as 400, 401, 403 and 404, since repeating the same request gives the same result.

**Q: What is exponential backoff with jitter?** Waiting twice as long after each failure, plus a random amount, so many clients do not retry at the same time.

**Q: What is a provider fallback?** Switching to a second model or provider when the first one fails or is too slow.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Stream an answer and print how many seconds passed until the first piece and until the last.
2. Write a fake stream (a list of objects with `.choices[0].delta.content`) and test a function that joins them.
3. Write a test showing that `call_with_retry` tries a `BadRequestError` exactly once.
4. Make `call_with_retry` honour a `retry_after` value when the error carries one.
5. Add logging of the attempt number and the wait time.
6. **Think:** why can retries make an outage worse, and how do backoff and jitter help?
:::
