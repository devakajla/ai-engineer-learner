# 13. Streaming: SSE and WebSockets

Normally a response is sent **all at once**. For an LLM answer that takes 20 seconds, the user would stare at a blank screen. With **streaming**, you send pieces as they are ready, and the text appears word by word, like ChatGPT.

Two tools:

| Tool | Direction | Best for |
| --- | --- | --- |
| **SSE** (Server-Sent Events) | server to client, one way | LLM answers, progress, live notifications |
| **WebSocket** | both ways, stays open | chat, games, live collaboration |

For LLM text, **SSE is usually the right choice**: it is simpler, works over normal HTTP, and reconnects by itself.

## SSE: the idea

The server keeps the connection open and sends lines of text in a fixed format:

```
data: "Hel"

data: "lo"

data: "!"

```

Each message is a `data:` line followed by a blank line. The browser's `EventSource` reads them one by one.

## Steps

::: {.step}
Step 1: a first stream with a counter
:::

Recent FastAPI versions have built-in SSE support. Create `app/api/routes/stream.py`:

```python
import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/count", response_class=EventSourceResponse)
async def count() -> AsyncIterator[int]:
    for i in range(1, 6):
        yield i
        await asyncio.sleep(1)
```

Two things make this streaming:

- `response_class=EventSourceResponse` sets the SSE content type.
- The function uses **`yield`** instead of `return`. Each `yield` sends one event.

Include the router, then watch it arrive:

```bash
curl -N localhost:8000/api/v1/stream/count
# data: 1
#
# data: 2
#   ...one line every second...
```

`-N` turns off curl's buffering so you see events as they come. Each value is JSON-encoded (a string `"hello"` is sent as `data: "hello"` with quotes).

::: {.step}
Step 2: stream an LLM answer
:::

LLM libraries can return the answer in small pieces ("chunks"). We pass them on. First, a service that works with **any** client (so tests can use a fake one). `app/services/llm_service.py`:

```python
from collections.abc import AsyncIterator

SYSTEM_PROMPT = "You are a helpful assistant for a task manager app. Answer briefly."


async def stream_answer(client, model: str, question: str) -> AsyncIterator[str]:
    """Yield the answer piece by piece. `client` is an AsyncGroq (or a fake in tests)."""
    stream = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        stream=True,
        max_completion_tokens=300,
        timeout=30,
    )
    async for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece
```

Then the route. `app/api/routes/chat.py`:

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.sse import EventSourceResponse
from groq import AsyncGroq

from app.api.deps import CurrentUser
from app.core.config import Settings, get_settings
from app.services.llm_service import stream_answer

router = APIRouter(prefix="/chat", tags=["chat"])


def get_llm_client(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncGroq:
    return AsyncGroq(api_key=settings.groq_api_key)


@router.get("/stream", response_class=EventSourceResponse)
async def chat_stream(
    user: CurrentUser,
    client: Annotated[AsyncGroq, Depends(get_llm_client)],
    settings: Annotated[Settings, Depends(get_settings)],
    question: Annotated[str, Query(min_length=1, max_length=500)],
) -> AsyncIterator[str]:
    async for piece in stream_answer(client, settings.groq_model, question):
        yield piece
```

Install the SDK and add the key to `.env` (never in code):

```bash
uv add groq
```

```
GROQ_API_KEY=gsk_...your key from console.groq.com
```

(Add `groq_api_key: str = ""` and `groq_model: str = "llama-3.1-8b-instant"` to `Settings`. Model names change, so check console.groq.com/docs/models.)

Why this design?

- The **LLM client is a dependency** (`get_llm_client`). A test replaces it with a fake that needs no network and no key.
- The **service** knows nothing about HTTP. The route only passes pieces through.
- The route requires login (`CurrentUser`), so strangers cannot spend your money.

```bash
curl -N "localhost:8000/api/v1/chat/stream?question=Say%20hi" -H "Authorization: Bearer $TOKEN"
# data: "Hello"
#
# data: "!"
#   ... pieces arrive as the model writes them
```

::: {.step}
Step 3: read it in a browser
:::

```javascript
const source = new EventSource("/api/v1/chat/stream?question=Hi");
source.onmessage = (event) => {
  output.textContent += JSON.parse(event.data);   // add each piece
};
source.onerror = () => source.close();
```

> **Catch:** the browser's `EventSource` cannot send an `Authorization` header. For browser clients, either send the token in a cookie, use `fetch()` with a streaming reader, or use a short-lived token in the query string. This is a common real-world problem.

## `StreamingResponse`: the general tool

SSE is one format. For anything else (a big CSV, a file), return a generator through `StreamingResponse`:

```python
from fastapi.responses import StreamingResponse

async def csv_rows():
    yield "id,title\n"
    for task in await load_all_tasks():
        yield f"{task.id},{task.title}\n"

@router.get("/export")
async def export():
    return StreamingResponse(csv_rows(), media_type="text/csv")
```

Memory stays small because rows are sent one by one, never all at once.

## WebSockets

A WebSocket is a **two-way** connection that stays open. The client and server can both send at any time.

`app/api/routes/ws.py`:

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_text(f"you said: {text}")
    except WebSocketDisconnect:
        pass
```

Include it in `main.py` with `app.include_router(ws.router)`. Test with `uv run python -c` and the `websockets` package (installed by `fastapi[standard]`):

```python
import asyncio, websockets

async def main():
    async with websockets.connect("ws://localhost:8000/ws/echo") as ws:
        await ws.send("hi")
        print(await ws.recv())     # -> you said: hi

asyncio.run(main())
```

A **chat room** needs a manager that remembers who is connected and sends a message to all:

```python
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for ws in self.active:
            await ws.send_text(message)
```

> This keeps connections in the memory of **one** process. With several servers, a message must travel through something shared, like Redis pub/sub. Keep this in mind for system design.

## SSE or WebSocket?

| | SSE | WebSocket |
| --- | --- | --- |
| Direction | server → client | both |
| Protocol | plain HTTP | its own upgrade |
| Reconnect | automatic | you write it |
| Auth headers | tricky in browsers | tricky too (use a token in the first message) |
| Pick it for | LLM tokens, progress bars | chat, multiplayer |

## Things to watch in streaming

- **Errors after the stream starts.** The status code `200` was already sent. You cannot change it. Send an error event instead, and end the stream.
- **Client disconnects.** Stop the work (do not keep paying for LLM tokens nobody reads). Cancelling the loop usually does this.
- **Proxies and buffering.** Nginx may hold your stream back. Turn buffering off for these routes (`X-Accel-Buffering: no`).
- **Timeouts.** Set a timeout on the LLM call (we used `timeout=30`).

::: {.box .checkpoint}
**Folder now**

```
app/
├── services/llm_service.py        # NEW: stream_answer
└── api/routes/
    ├── stream.py                  # NEW: /stream/count
    ├── chat.py                    # NEW: /chat/stream (SSE from an LLM)
    └── ws.py                      # NEW: /ws/echo
```

**Checkpoint:** `curl -N .../stream/count` prints one number per second. The WebSocket echo replies `you said: hi`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Building the whole text first and sending it at the end. That is not streaming.
- Using a blocking call inside the streaming generator.
- Calling the LLM with no timeout.
- Leaving the streaming route open to anonymous users.
- Forgetting that the status code is already sent once streaming starts.
- Keeping WebSocket connections in server memory and then running several servers.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: SSE vs WebSocket?**
SSE is one-way (server to client) over plain HTTP with automatic reconnect, ideal for LLM token streaming. WebSocket is two-way and suits chat and games.

**Q: How do you stream an LLM response with FastAPI?**
Call the model with `stream=True`, loop over the chunks in an async generator, and return it with `EventSourceResponse` (or `StreamingResponse`).

**Q: What happens if an error occurs mid-stream?**
The status code is already sent, so you emit an error event and close the stream.

**Q: How do you scale WebSockets across servers?**
Put a shared broker (Redis pub/sub) between servers so a message reaches clients on every server.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Change `/stream/count` to count from 1 to 10 and send each number with the event name `"tick"` using `ServerSentEvent(data=i, event="tick")`.
2. Write a fake LLM client (a class with an async `create` method) that returns three chunks, and use it to test `stream_answer` without the network.
3. Build `/export` that streams all of the current user's tasks as CSV.
4. Add a `ConnectionManager` chat room at `/ws/chat` and test it with two terminals.
5. **Think:** why is it a problem to stream an LLM answer to a user who has already closed the page?
:::
