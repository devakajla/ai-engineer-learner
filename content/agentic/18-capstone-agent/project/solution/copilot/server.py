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
