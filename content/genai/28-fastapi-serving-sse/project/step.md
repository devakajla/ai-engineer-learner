# Step 24 — Serve Copilot over HTTP, and stream the answer

Until now Copilot ran in your terminal. A product needs an **HTTP API**. Models are slow (seconds), so waiting for the full answer feels broken. **Streaming** sends the text piece by piece, so the first words appear at once. You build both with FastAPI and **server-sent events** (SSE), as in lesson 28.

Your folder after this step (new files marked):

```
devdocs-copilot/
├── pyproject.toml      <- adds fastapi and uvicorn
└── copilot/
    ├── server.py       <- new
    └── ... (all files from step 23)
```

Add `"fastapi>=0.115"` and `"uvicorn>=0.30"` to the dependencies, then run `uv sync`.

### 1. `copilot/server.py`

```python
"""Serve Copilot over HTTP: a JSON endpoint, and a streaming endpoint that uses server-sent events (SSE)."""

import json

from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import NO_ANSWER, answer as rag_answer, build_rag_messages, retrieve


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


def create_app(client, collection, embed=embed_texts, model=DEFAULT_MODEL):
    """Build the app. The client and the collection live on app.state, so tests can pass fakes."""
    app = FastAPI(title="DevDocs Copilot")
    app.state.client = client
    app.state.collection = collection
    app.state.embed = embed
    app.state.model = model

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ask")
    def ask(request: Request, question: str = Query(min_length=1, max_length=2000)):
        state = request.app.state
        result = rag_answer(state.client, state.collection, question, embed=state.embed, model=state.model)
        return {"answer": result["answer"], "sources": [hit["id"] for hit in result["hits"]]}

    @app.get("/stream")
    def stream(request: Request, question: str = Query(min_length=1, max_length=2000)):
        state = request.app.state
        events = ask_events(state.client, state.collection, question, embed=state.embed, model=state.model)
        return StreamingResponse(
            events,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app


def build_default_app():
    """For uvicorn --factory: the real client and the real index."""
    from copilot.llm import get_client
    from copilot.store import open_collection

    return create_app(get_client(), open_collection(".chroma"))
```

Read it in parts:

1. **SSE is plain text.** One message is some lines like `event: token` and `data: hello`, then **a blank line**. The browser's `EventSource` reads them. `format_sse` adds `data:` to **every** line, because a bare newline inside data would end the message too early.
2. **`chunk_text`** gets the new text from one chunk. Providers send keep-alive chunks with no `choices` or with `content=None`. Treat them as empty text.
3. **`sse_stream`** is a **generator** (it uses `yield`). It sends each piece as a `token` event. A generator is the right tool for streaming because the next piece is only made when the client is ready for it. If the model fails in the middle, the HTTP status is already `200`, so you cannot change it. The failure becomes an `error` **event** instead, and the stream stops there. Every stream ends with **exactly one** `done` or `error` event, so the client always knows that it is over.
4. **`ask_events`** is the whole answer for one question. It sends the **sources first**, as a `sources` event holding the chunk ids. The user can see where the answer comes from before the text arrives. No hits means no model call: it sends "I don't know." and `done`.
5. **`create_app`** builds the app and puts the client, the collection and the embedder on **`app.state`**. Handlers read them from `request.app.state`. Tests pass fakes, and the real code passes real objects. No globals, no import-time work.
6. **`/ask`** returns JSON with the answer and the sources (use it for scripts). **`/stream`** returns a `StreamingResponse` with `media_type="text/event-stream"`. `Cache-Control: no-cache` stops caches from holding the stream. `X-Accel-Buffering: no` tells nginx not to buffer it (a buffered stream arrives all at once).
7. **`Query(min_length=1, max_length=2000)`** checks the question. An empty or huge question gets a `422` before any model call. This is the first cheap guard against abuse and cost.
8. **`build_default_app`** is for `uvicorn --factory`. It imports `get_client` and `open_collection` inside the function, so importing the module never needs the key or the database.

### 2. Run it

```
uv run uvicorn copilot.server:build_default_app --factory --port 8100
curl -N "http://localhost:8100/stream?question=how%20do%20I%20delete%20a%20task"
```

`-N` turns off curl's buffering, so you can watch the pieces arrive. Open `http://localhost:8100/docs` to try `/ask`.

> Two things to remember for production: the **client may disconnect** while the model is still working (stop the work if you can), and **errors after the first byte** can only be sent as events. Test both.

### Checkpoint

Run the tests. Then start the server, call `/stream` with curl, and check that the `sources` event comes first and that the text arrives in pieces. Stop the server in the middle of a stream and check what curl shows.
