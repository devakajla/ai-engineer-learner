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
