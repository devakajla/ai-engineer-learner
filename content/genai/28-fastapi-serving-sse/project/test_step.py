"""Step 24 checks. Runs with the current directory = the learner's project folder."""

import json
import uuid
from types import SimpleNamespace as NS

from fastapi.testclient import TestClient

from copilot.server import ask_events, chunk_text, create_app, format_sse, sse_stream
from copilot.store import add_chunks, open_collection
from copilot.tracing import percentile


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id")]


def piece(text):
    return NS(choices=[NS(delta=NS(content=text))])


class FakeClient:
    """Plain calls return a full reply. stream=True returns the prepared pieces (an Exception inside stops it)."""

    def __init__(self, pieces=("Use ", "DELETE ", "[1]."), full="Use DELETE [1]."):
        self.pieces, self.full = pieces, full
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs.get("stream"):
            return self._generate()
        return NS(choices=[NS(message=NS(content=self.full))])

    def _generate(self):
        for p in self.pieces:
            if isinstance(p, Exception):
                raise p
            yield piece(p)


def filled(chunks=CHUNKS):
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    if chunks:
        add_chunks(collection, chunks, embed=embed)
    return collection


def parse(text):
    """Split an SSE body into [(event, data)]."""
    out = []
    for block in text.strip().split("\n\n"):
        event, data = "message", []
        for line in block.split("\n"):
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data.append(line[6:])
        out.append((event, "\n".join(data)))
    return out


def test_earlier_steps_still_work():
    assert percentile([1, 2, 3], 50) == 2


def test_format_sse():
    assert format_sse("hi") == "data: hi\n\n"
    assert format_sse("hi", "token") == "event: token\ndata: hi\n\n"
    assert format_sse("a\nb") == "data: a\ndata: b\n\n", "every line needs its own data: prefix"


def test_chunk_text_ignores_keep_alives():
    assert chunk_text(piece("x")) == "x"
    assert chunk_text(piece(None)) == ""
    assert chunk_text(NS(choices=[])) == ""


def test_sse_stream_ends_with_done():
    events = list(sse_stream([piece("a"), piece(None), piece("b")]))
    assert events == ["event: token\ndata: a\n\n", "event: token\ndata: b\n\n", "event: done\ndata: [DONE]\n\n"]


def test_sse_stream_turns_a_midstream_failure_into_an_error_event():
    client = FakeClient(pieces=("a", RuntimeError("cut"), "b"))
    events = list(sse_stream(client.chat.completions.create(stream=True)))
    assert events == ["event: token\ndata: a\n\n", "event: error\ndata: stream failed: cut\n\n"]


def test_ask_events_sends_the_sources_first():
    client = FakeClient()
    events = parse("".join(ask_events(client, filled(), "how do I delete a task", embed=embed)))
    assert events[0] == ("sources", json.dumps(["tasks.md:0"]))
    assert [e for e, _ in events[1:]] == ["token", "token", "token", "done"]
    assert "".join(d for e, d in events if e == "token") == "Use DELETE [1]."
    assert client.calls[0]["stream"] is True and client.calls[0]["temperature"] == 0


def test_no_hits_means_no_model_call():
    client = FakeClient()
    events = parse("".join(ask_events(client, filled([]), "anything", embed=embed)))
    assert events == [("sources", "[]"), ("token", "I don't know."), ("done", "[DONE]")]
    assert client.calls == []


def make_app(client=None, chunks=CHUNKS):
    return TestClient(create_app(client or FakeClient(), filled(chunks), embed=embed))


def test_health():
    assert make_app().get("/health").json() == {"status": "ok"}


def test_json_endpoint():
    response = make_app().get("/ask", params={"question": "how do I delete a task"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Use DELETE [1].", "sources": ["tasks.md:0"]}


def test_question_is_checked():
    app = make_app()
    assert app.get("/ask").status_code == 422
    assert app.get("/ask", params={"question": ""}).status_code == 422
    assert app.get("/stream", params={"question": "x" * 2001}).status_code == 422


def test_stream_endpoint_is_server_sent_events():
    response = make_app().get("/stream", params={"question": "how do I delete a task"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache"
    events = parse(response.text)
    assert events[0][0] == "sources" and events[-1] == ("done", "[DONE]")
    assert "".join(d for e, d in events if e == "token") == "Use DELETE [1]."


def test_a_failing_model_still_gives_a_clean_stream():
    app = make_app(FakeClient(pieces=("Use ", RuntimeError("model died"))))
    response = app.get("/stream", params={"question": "how do I delete a task"})
    assert response.status_code == 200
    assert parse(response.text)[-1] == ("error", "stream failed: model died")
