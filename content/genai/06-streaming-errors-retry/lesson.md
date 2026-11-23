---
title: Streaming, errors, timeouts and retries
summary: Show the answer as it is written with streaming, and make your calls safe against errors, slow replies and rate limits.
plan_ids: []
---

When you call an API, you depend on computers far away and on the network between you and them. Things can be slow. Things can break. A beginner's program assumes everything works. A real program **expects problems** and handles them.

Two problems in this lesson:

1. A long answer can take many seconds. The user stares at a blank screen.
2. Calls sometimes fail. The network drops, the service is busy, or you send too many requests.

**Streaming** fixes the first. **Timeouts and retries** fix the second. Both are part of every serious AI app.

## Streaming

Without streaming, you wait for the **whole** answer, then see it all at once. With streaming, the model sends the answer in small pieces while it writes. You show each piece at once, like ChatGPT does.

The total time is about the same. But the first words appear in a fraction of a second, so the app *feels* much faster. The wait for the first word is the **time to first token** (lesson 2).

Add `stream=True`:

```python
stream = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "Count from 1 to 5."}],
    stream=True,
)

for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)
# -> 1, 2, 3, 4, 5
```

What is new here:

- With `stream=True` you do not get one `response`. You get a **stream**: something you loop over with `for`. Each item is a **chunk**.
- A chunk has `choices[0].delta.content`. **delta** means "the new part". It is a small piece of text.
- The text piece can be `None`. For example, the first chunk only says "the assistant is talking", and the last one only says "finished". Always check before you use it.
- `print(piece, end="", flush=True)` prints without a new line (`end=""`) and shows the text now (`flush=True`) instead of waiting.

### Step by step: join the pieces

Often you want the full text as well. Collect the pieces, skip the `None`, and join:

1. Make an empty list `kept`.
2. Loop over the pieces. If a piece is not `None`, add it.
3. Join the list into one string with `"".join(kept)`.

```python
def join_pieces(pieces):
    kept = []
    for p in pieces:
        if p is not None:
            kept.append(p)
    return "".join(kept)

join_pieces(["Hel", None, "lo", " there"])   # -> 'Hello there'
join_pieces([])                              # -> ''
```

In the first exercise the pieces are inside chunks, and some chunks have no `choices` at all. You will handle that too.

## Things that go wrong

Many things can fail. The SDK raises an **exception** for each (you met exceptions in Python level 1). The important ones:

| Problem | HTTP code | SDK exception | Retry? |
| --- | --- | --- | --- |
| Bad request (wrong parameter, input too long) | 400 | `BadRequestError` | No, fix your code |
| Bad or missing key | 401 | `AuthenticationError` | No, fix the key |
| Model not found | 404 | `NotFoundError` | No, fix the name |
| Too many requests (rate limit) | 429 | `RateLimitError` | Yes, after a wait |
| Server problem | 500 and up | `InternalServerError` | Yes |
| No connection or too slow | - | `APIConnectionError`, `APITimeoutError` | Yes |

The **HTTP code** is a number the server sends with every reply. 200 means success. Numbers starting with 4 mean *you* made a mistake. Numbers starting with 5 mean *the server* had a problem.

The rule: **retry only problems that can go away by themselves.** A wrong key stays wrong, no matter how often you try.

```python
import groq

try:
    text = ask(client, "Hi")
except groq.RateLimitError:
    print("Slow down, try again later")
except groq.APIConnectionError:
    print("Cannot reach Groq")
```

To handle several errors the same way, put them in a tuple:

```python
except (groq.RateLimitError, groq.APIConnectionError, groq.InternalServerError):
    ...
```

## Timeouts

A **timeout** is how long you wait before giving up. Without one, a stuck call can freeze your app.

```python
client = Groq(api_key=key, timeout=20.0)                          # for every call
client.with_options(timeout=5.0).chat.completions.create(...)     # for one call
```

The SDK already has defaults, and it already retries twice (`max_retries=2`) on some errors. For production you set your own values.

## Retries with backoff

If a call fails because the server is busy, trying again at once often fails again. So you **wait a little, then try again, and wait longer each time**. This is **exponential backoff**: the wait doubles.

```
try 1 fails -> wait 1 s
try 2 fails -> wait 2 s
try 3 fails -> wait 4 s
```

The waits are `base * 2 ** attempt`. Here `**` means "to the power of", so `2 ** 3` is `8`. Put a cap on it, so you never wait too long:

```python
delays = [min(1 * 2**i, 30) for i in range(5)]
print(delays)   # -> [1, 2, 4, 8, 16]
```

`min(a, b)` gives the smaller of the two. The cap keeps the wait from growing past 30 seconds.

Now the retry loop. The idea in plain steps:

1. Loop `max_tries` times.
2. Inside, `try` the action. If it works, **return** right away.
3. If it fails, remember the error. Then go round again.
4. After the loop, nothing worked. Raise the last error.

A small example with a different action: return the first text that turns into a number.

```python
def first_int(texts):
    last_error = None
    for text in texts:
        try:
            return int(text)
        except ValueError as e:
            last_error = e
    raise last_error

first_int(["a", "b", "7"])   # -> 7
first_int(["x", "y"])        # raises ValueError: invalid literal for int() with base 10: 'y'
```

The pattern is: *try, return on success, remember the error, raise at the end*.

The real retry for an API call has `client.chat.completions.create(...)` inside the `try`, and a wait between tries with `time.sleep(seconds)`. For tests we do not want to wait. So the function takes a `sleep` argument: a function to call with the wait time. A test passes a fake that only records the time. Real code passes `time.sleep`. You will build this in the third exercise, with your backoff function from the second one.

## Try it live

1. Stream a long answer (ask for a 200-word story). Watch the words appear.
2. Break your key on purpose (`GROQ_API_KEY=wrong`) and run a call. Which exception do you get? Would you retry it?
3. Set `timeout=0.001` and run a call. Which exception do you get now?

## A little deeper

- **Jitter.** If 1000 clients all wait exactly 2 seconds and retry together, they hit the server together again. Add a small random amount to each wait to spread them out.
- **Retry-After.** On a 429, the response often says how long to wait (a `Retry-After` header). Respect it when you can.
- **Retries can cost money.** A call that fails after the model started working may still be billed. Do not retry without limits.
- **Streams can break halfway.** You may have shown part of the answer already. Decide what to do: show an error, or retry and start the answer over.
- **Fallback model.** If the big model keeps failing, you can try a smaller one (lesson 33). This keeps the app up, at lower quality.
- **Circuit breaker.** If a service fails again and again, stop calling it for a while, instead of making things worse.
- **Time to first token** (TTFT) is the wait before the first piece arrives. It is the number that decides how fast streaming *feels*.

## Common mistakes

- Retrying errors like 401 or 400. They will never work.
- Retrying with no wait, or with no limit on the number of tries.
- Not setting a timeout, so one slow call hangs the app.
- Catching every exception and hiding real bugs. Catch the specific ones you can handle.
- Using the text piece without checking for `None`.
- Forgetting `flush=True`, so the text appears only at the end.

## Interview corner

**What is streaming and why use it?**
The server sends the answer in pieces while the model writes it. The first words show quickly, so the app feels fast, even if the total time is the same.

**Which errors do you retry?**
Rate limits (429), server errors (5xx), timeouts and connection errors. Not client errors like 400, 401 and 404, because retrying will not fix them.

**What is exponential backoff with jitter?**
Wait longer after each failure (1, 2, 4, 8 seconds), and add a random amount, so many clients do not retry at the same moment.

**What is a timeout and why is it needed?**
A limit on how long to wait for a reply. Without it, a stuck request can block your app forever.

## Summary

- `stream=True` gives chunks. Text is in `chunk.choices[0].delta.content`, which can be `None`.
- Retry only errors that can go away: 429, 5xx, timeouts and connection errors.
- Set a timeout. Use exponential backoff: wait `base * 2 ** attempt`, with a cap.
- Retry loop: try, return on success, remember the error, raise the last one at the end.
- Project: step 3 adds retries, streaming and a small command-line chat to DevDocs Copilot.
- Reference: `reference/genai-groq.md`.
