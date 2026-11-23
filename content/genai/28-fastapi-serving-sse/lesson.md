---
title: Serving an LLM with FastAPI and streaming (SSE)
summary: Put your model behind a web API, send the answer token by token with server-sent events, and handle slow calls, errors in the middle of a stream and closed connections.
plan_ids: []
---

Until now your code ran in a terminal. Real users reach it through a web app. So your Python code becomes a **web service** (an API), and a browser or a mobile app calls it.

There is one problem that is special for LLMs: they are **slow**. A full answer can take 5 to 30 seconds. If the user stares at a blank screen for 20 seconds, they leave. The fix is the same one ChatGPT uses: show the answer **while it is written**, word by word. This is **streaming**.

> This lesson uses FastAPI. You learn FastAPI properly in the FastAPI track. Here you only copy a small, working shape. The graded exercises use plain Python, no web server needed.

## Why streaming matters

Two different times:

- **Time to first token**: how long until the user sees the first word.
- **Total time**: how long until the answer is complete.

Streaming does not make the total time shorter. It makes the **first token** arrive fast (often under a second), so the app **feels** fast. For chat apps this is the biggest quality-of-life feature you can add.

You already know the model side (lesson 6): with `stream=True` the SDK gives you many small **chunks**, and each chunk holds a piece of text. The new question: how do you pass these pieces on to the browser?

## Ways to push data to a browser

| Way | How it works | Good for |
| --- | --- | --- |
| **Normal request** | Wait for everything, send once | Short answers, background jobs |
| **Polling** | Browser asks again and again: "ready?" | Very simple jobs, but wasteful |
| **SSE** (server-sent events) | One HTTP connection stays open. Server sends text events. One way: server to browser | **LLM token streams**, progress, notifications |
| **WebSocket** | A two-way connection | Voice, games, collaborative editing, live two-way chat |

For LLM text streaming, **SSE is the usual choice**. It is plain HTTP, easy to debug, works through most proxies, and the browser can reconnect by itself. Use WebSockets only when the client must also send data all the time over the same connection.

## What an SSE message looks like

SSE is just text with a simple rule: each event is a few lines, and an **empty line** ends the event.

```
event: token
data: Hello

event: token
data:  there

event: done
data: [DONE]

```

- `event:` is the name of the event (optional). Your front-end code listens by name.
- `data:` is the content. A line break is not allowed inside a `data:` line, so text with several lines becomes several `data:` lines.
- The blank line ends the event.

A detail that surprises people: after `data:` the spec removes **one** space. So `data:  there` (two spaces) means the text `" there"`, with one leading space. The model puts the spaces at the **start** of words, so keep them.

### Step by step: build one event

Let's practise the shape of the first exercise with a different example: format a chat line for a log file. Each line is `"[level] message"`, and a message with several lines gets the prefix on **every** line, with a blank line at the end.

1. Split the message into lines.
2. Put the prefix in front of each line.
3. Join with `"\n"` and add the final blank line.

```python
def format_log(level, message):
    lines = []
    for line in message.split("\n"):
        lines.append("[" + level + "] " + line)
    return "\n".join(lines) + "\n\n"

print(repr(format_log("info", "a\nb")))   # -> '[info] a\n[info] b\n\n'
```

`format_sse` is the same idea: prefix each line (`data: `), maybe add one `event:` line first, join, and end with a blank line.

## A streaming endpoint in FastAPI

Here is a complete small server. It does not call a real model: `fake_tokens` stands in for it, so you can run it with no key.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


def fake_tokens():
    for word in ["Hello", " there", "!"]:
        yield word


def sse_stream():
    try:
        for word in fake_tokens():
            yield "event: token\ndata: " + word + "\n\n"
    except Exception as error:
        yield "event: error\ndata: " + str(error) + "\n\n"
        return
    yield "event: done\ndata: [DONE]\n\n"


@app.get("/chat/stream")
def chat_stream():
    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

Calling it with FastAPI's test client gave this (real output):

```
200 text/event-stream; charset=utf-8
'event: token\ndata: Hello\n\nevent: token\ndata:  there\n\nevent: token\ndata: !\n\nevent: done\ndata: [DONE]\n\n'
```

What just happened:

- A function with `yield` is a **generator**. Instead of returning everything at once, it hands out one piece at a time and waits to be asked for the next. (Copy the shape for now.) That is exactly what streaming needs.
- `StreamingResponse` takes a generator and sends each piece to the client as soon as it is produced.
- `media_type="text/event-stream"` tells the browser that this is SSE.
- `Cache-Control: no-cache` stops caches from holding the stream.
- `X-Accel-Buffering: no` tells nginx not to collect the whole answer before sending it. A proxy that buffers breaks streaming: the user sees nothing and then everything at the end. This is the number one "why does my stream not stream?" problem.

To use the real model, replace `fake_tokens` with a loop over the Groq stream: `for chunk in stream: text = chunk.choices[0].delta.content`, and `yield` the non-empty texts.

## Reading a chunk safely

Real chunks are messy. `delta.content` can be `None` in the first or last chunk, and some providers send a last chunk with **no choices** (only token counts). Always write one small helper that turns any chunk into text or an empty text:

```python
def chunk_text(chunk):
    if not chunk.choices:
        return ""
    text = chunk.choices[0].delta.content
    if text is None:
        return ""
    return text
```

That is exercise 2. Your own code then never has to think about these cases again. (Lesson 6 showed that the final chunk may also hold the usage. If you want to log the token count of a streamed answer, read it there.)

## The end of the stream and errors in the middle

Two things the browser must know:

1. **When it is finished.** Send a last `done` event. Without it the browser cannot tell "finished" from "connection broke".
2. **When it broke.** Once you have sent the first piece, the HTTP status `200` has already gone out. You can no longer return a `500`. So errors in the middle must travel **inside the stream**, as an `error` event. The front-end listens for it and shows a message ("something went wrong, try again"). After an error, do **not** send `done`.

Errors at the **start** (a bad request, a missing login) are different: check them **before** you start the stream, and return a normal `401` or `422`.

Let's practise the "stop on error and report it" shape with a different example: read numbers from a list of texts. If one is not a number, stop there and report it. Do not add the "finished" marker in that case.

1. Loop inside `try`. Convert each item with `int(...)` and add it to the result.
2. In `except ValueError`, add an error line and return what you have.
3. If the loop ends normally, add the finished marker.

```python
def read_numbers(items):
    out = []
    try:
        for item in items:
            out.append("num " + str(int(item)))
    except ValueError as error:
        out.append("error: " + str(error))
        return out
    out.append("finished")
    return out

print(read_numbers(["1", "2"]))        # -> ['num 1', 'num 2', 'finished']
print(read_numbers(["1", "x", "3"]))   # -> ['num 1', "error: invalid literal for int() with base 10: 'x'"]
```

The `return` inside `except` is what prevents the `finished` line. Exercise 4 has the same shape.

## The browser side (short)

The browser has a ready tool, `EventSource`, that connects, receives events and reconnects by itself. But it can only send **GET** requests with no body. For chat you often want to send the messages as JSON, so people use `fetch` with a **POST** and read the response body as a stream, then split it at the blank lines. You do not need to write this now. Know the trade-off:

- `EventSource`: simple, auto-reconnect, GET only, hard to add an `Authorization` header.
- `fetch` + POST: any method and headers, you handle parsing and reconnects yourself.

## Other things a real LLM service needs

- **Timeouts.** Set a timeout on the model call (lesson 6) and on the whole request. A stuck call must not hold a worker forever.
- **Closed connections.** If the user closes the tab, stop the model call. Otherwise you keep paying for an answer nobody reads. (FastAPI can tell you the client disconnected. See the FastAPI track.)
- **Keep-alive.** Some proxies close a connection that is silent for 30 to 60 seconds. A comment line (`": ping\n\n"`, a line that starts with a colon) is ignored by the browser and keeps the line open.
- **Concurrency.** Each open stream holds a connection and a worker for many seconds. A normal (blocking) endpoint uses one thread per stream. Many users means many threads. The FastAPI track shows `async`, which handles many waiting connections with fewer resources. Load-test before you promise numbers.
- **Auth and limits.** The stream endpoint needs a login check **before** the model call, and a rate limit per user (lesson 29). An open endpoint that calls a paid model is a gift to attackers.
- **Do not put the API key in the browser.** The browser calls your server. Your server calls Groq. The key stays on the server.
- **Do not log secrets.** Log the request id, the model, token counts and timing (lesson 29), not the full prompts when they may hold personal data.

## Try it live

1. Save the example above as `server.py`. Run it: `uvicorn server:app --reload`.
2. In another terminal: `curl -N http://127.0.0.1:8000/chat/stream`. The `-N` flag turns off curl's own buffering. You see the events appear one by one.
3. Make `fake_tokens` slow: add `import time` and `time.sleep(0.5)` inside the loop. Watch the tokens arrive over two seconds.
4. Replace `fake_tokens` with a real Groq stream (`stream=True`). Yield the non-empty `delta.content` texts. Ask a long question.
5. Make it fail on purpose: raise an error in the middle (for example when the word is `"!"`). Do you see the `error` event and no `done`?
6. Remove the `X-Accel-Buffering` header and put nginx in front (if you have it) to see buffering. This step is optional.

## A little deeper

- **Server-sent events are one-way.** To let the user stop an answer, the browser simply closes the connection (or calls a second endpoint such as `POST /chat/cancel`).
- **Reconnect and resume.** SSE events can carry an `id:` line. After a reconnect the browser sends `Last-Event-ID`, so the server may resume. For LLM answers this is rarely worth it: you just retry the whole answer.
- **JSON inside `data:`.** Often each event holds a JSON text, for example `data: {"text": "Hello"}`. Then a leading space in the token is safe (it sits inside the JSON string), and you can send extra fields (token counts, ids) in the same event.
- **Structured streaming.** If the answer must be valid JSON (lesson 9), streaming shows half a JSON text. Stream plain text to the user, or validate at the end.
- **Backpressure.** If the client reads slowly, the server's buffer grows. For text this is small, but know the word.
- **Tool calls in a stream.** Agents (lesson 27) can stream the *events* of the loop too: "calling get_weather...", "got result...", then the answer tokens. It makes long agent runs feel alive.
- **Streaming and moderation.** Checking an answer for rules (lesson 30) is harder when you already sent half of it. Options: check the **input** before, stream, and check the **final** text after. Or buffer a few sentences before showing them.
- **WebSockets** need their own handling of login, reconnects and scaling. Pick them only when you need two-way traffic.

## Common mistakes

- A proxy that buffers the response, so nothing appears until the end (`X-Accel-Buffering: no`, and check your gateway).
- Forgetting `Cache-Control: no-cache`.
- Not handling `None` content or empty `choices` in a chunk.
- No `done` event, so the front-end cannot tell finished from broken.
- Trying to return an error status after the stream has started.
- Removing the leading space of tokens, so words stick together.
- No timeout, no login check, no rate limit on the stream endpoint.
- Calling Groq directly from the browser with the key in the page.
- Not stopping the model call when the user closed the page.

## Interview corner

**Why stream LLM responses?**
LLMs generate token by token and take seconds. Streaming shows the first tokens quickly, so the app feels fast even though the total time is the same.

**SSE or WebSocket for a chat app?**
SSE for token streams: one-way, plain HTTP, easy to proxy, automatic reconnect. WebSocket when you need real two-way messages over one connection (voice, live collaboration).

**What happens if the model call fails halfway through a stream?**
The `200` status is already sent. Send an `error` event inside the stream, do not send `done`, and let the client show a retry option. Log it on the server.

**Why does a stream sometimes arrive all at once?**
Something between the app and the user buffers the response: a proxy such as nginx, a CDN, or a compression middleware. Turn buffering off for that route (`X-Accel-Buffering: no`).

**What do you check before opening a stream?**
Authentication, input validation, rate limits and budget. Errors found after the first byte can only be sent as events.

## Summary

- Streaming makes the first token arrive fast, so the app feels fast. The total time does not change.
- SSE: one open HTTP connection, text events (`event:` and `data:` lines, a blank line ends the event). One way, server to browser. Best fit for LLM tokens. WebSockets are for two-way traffic.
- FastAPI: a generator with `yield` plus `StreamingResponse(media_type="text/event-stream")`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`.
- Read chunks safely: `content` can be `None`, and `choices` can be empty.
- Send a `done` event at the end. Errors in the middle travel as an `error` event, and no `done` follows.
- Check login, input and limits before the stream starts. Set timeouts. Stop the model call if the client disconnects.
- Keep the API key on the server.
- Reference: `reference/genai-groq.md`.
