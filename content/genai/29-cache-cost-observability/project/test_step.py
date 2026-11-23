"""Step 25 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from fastapi.testclient import TestClient

from copilot.cache import (
    EXAMPLE_PRICES,
    allow_request,
    cache_key,
    cached_call,
    cached_rag_answer,
    estimate_cost,
    summarize_calls,
)
from copilot.server import create_app, format_sse
from copilot.store import add_chunks, open_collection


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id")]


class FakeClient:
    def __init__(self, text="Use DELETE [1].", fail=False):
        self.text, self.fail = text, fail
        self.calls = 0
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("model down")
        usage = NS(prompt_tokens=1000, completion_tokens=200)
        return NS(choices=[NS(message=NS(content=self.text))], usage=usage)


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 0.1
        return self.t


def filled(chunks=CHUNKS):
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, chunks, embed=embed)
    return collection


def test_earlier_steps_still_work():
    assert format_sse("x") == "data: x\n\n"


def test_cache_key_is_stable_and_sensitive():
    messages = [{"role": "user", "content": "hi"}]
    assert cache_key("m", messages, 0) == cache_key("m", [{"content": "hi", "role": "user"}], 0)
    assert cache_key("m", messages, 0) != cache_key("m", messages, 0.7)
    assert cache_key("m", messages, 0) != cache_key("other", messages, 0)
    assert len(cache_key("m", messages, 0)) == 16


def test_cached_call_saves_only_temperature_zero():
    cache, client = {}, FakeClient()
    messages = [{"role": "user", "content": "hi"}]
    assert cached_call(cache, client, messages) == {"text": "Use DELETE [1].", "cached": False}
    assert cached_call(cache, client, messages) == {"text": "Use DELETE [1].", "cached": True}
    assert client.calls == 1
    cached_call(cache, client, messages, temperature=0.7)
    cached_call(cache, client, messages, temperature=0.7)
    assert client.calls == 3, "creative calls are never cached"


def test_cached_call_records_real_calls_only():
    cache, calls, client = {}, [], FakeClient()
    messages = [{"role": "user", "content": "hi"}]
    cached_call(cache, client, messages, calls=calls, clock=Clock())
    cached_call(cache, client, messages, calls=calls, clock=Clock())
    assert calls == [{"model": "qwen/qwen3.8-27b", "input": 1000, "output": 200, "ms": 100, "ok": True}]


def test_a_failed_call_is_recorded_and_raised():
    calls = []
    try:
        cached_call({}, FakeClient(fail=True), [{"role": "user", "content": "q"}], calls=calls, clock=Clock())
        raise AssertionError("the error must be raised")
    except RuntimeError:
        pass
    assert calls == [{"model": "qwen/qwen3.8-27b", "input": 0, "output": 0, "ms": 100, "ok": False}]


def test_cached_rag_answer_key_includes_the_chunks():
    cache, client = {}, FakeClient()
    collection = filled()
    first = cached_rag_answer(cache, client, collection, "how do I delete a task", embed=embed)
    second = cached_rag_answer(cache, client, collection, "how do I delete a task", embed=embed)
    assert (first["cached"], second["cached"], client.calls) == (False, True, 1)
    add_chunks(collection, [chunk(1, "tasks.md", "Delete more", "delete a task also with the delete button")], embed=embed)
    third = cached_rag_answer(cache, client, collection, "how do I delete a task", embed=embed)
    assert third["cached"] is False, "new docs must not return an old answer"


def test_no_hits_means_no_call_and_no_cache():
    cache, client = {}, FakeClient()
    out = cached_rag_answer(cache, client, filled([]), "anything", embed=embed)
    assert out == {"answer": "I don't know.", "hits": [], "cached": False}
    assert client.calls == 0 and cache == {}


def test_allow_request_sliding_window():
    stamps = []
    for now in (0, 1, 2):
        verdict = allow_request(stamps, now, limit=3, window=10)
        assert verdict["allowed"] is True
        stamps = verdict["timestamps"]
    blocked = allow_request(stamps, 3, limit=3, window=10)
    assert blocked == {"allowed": False, "timestamps": [0, 1, 2], "retry_after": 7}
    assert allow_request(stamps, 10.5, limit=3, window=10)["allowed"] is True, "old requests leave the window"


def test_estimate_cost_and_summary():
    assert estimate_cost(1_000_000, 500_000, 0.30, 0.60) == 0.6
    calls = [
        {"model": "m", "input": 1000, "output": 1000, "ms": 100, "ok": True},
        {"model": "m", "input": 0, "output": 0, "ms": 300, "ok": False},
        {"model": "free", "input": 5, "output": 5, "ms": 200, "ok": True},
    ]
    summary = summarize_calls(calls, {"m": (1.0, 2.0)})
    assert summary == {"n": 3, "errors": 1, "error_rate": 0.3333, "total_cost": 0.003, "avg_ms": 200.0, "p95_ms": 300, "unpriced": 1}
    assert summarize_calls([], {})["n"] == 0
    assert "qwen/qwen3.8-27b" in EXAMPLE_PRICES


def make_app(client=None, limit=20, chunks=CHUNKS):
    clock = Clock()
    return TestClient(create_app(client or FakeClient(), filled(chunks), embed=embed, limit=limit, window=60, clock=clock))


def test_server_caches_and_reports_stats():
    client = FakeClient()
    app = make_app(client)
    first = app.get("/ask", params={"question": "how do I delete a task"}).json()
    second = app.get("/ask", params={"question": "how do I delete a task"}).json()
    assert first["cached"] is False and second["cached"] is True and client.calls == 1
    stats = app.get("/stats").json()
    assert stats["n"] == 1 and stats["errors"] == 0 and stats["total_cost"] > 0


def test_server_limits_requests_per_client():
    app = make_app(limit=2)
    codes = [app.get("/ask", params={"question": "how do I delete a task"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    blocked = app.get("/ask", params={"question": "how do I delete a task"})
    assert blocked.status_code == 429 and int(blocked.headers["retry-after"]) >= 1
    assert app.get("/health").status_code == 200, "health checks are not limited"
