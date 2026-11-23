"""Step 17 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.access import filter_hits
from copilot.context import answer_prepared, dedupe_hits, prepare_context, retrieve_prepared
from copilot.failures import CATEGORIES, classify_failure, failure_report
from copilot.store import add_chunks, open_collection


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def hit(i, source="a.md", text=None):
    return {"id": f"h{i}", "source": source, "heading": "", "text": text or f"text {i}"}


class FakeClient:
    def __init__(self, text="Done [1]."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return NS(choices=[NS(message=NS(content=self.text))])


def test_earlier_steps_still_work():
    assert filter_hits([{"tenant": "a", "groups": []}], {"tenant": "a"}) == [{"tenant": "a", "groups": []}]


def test_dedupe_removes_repeats_ignoring_case_and_spacing():
    hits = [hit(1, text="Use  POST"), hit(2, text="use post"), hit(3, text="other")]
    assert [h["id"] for h in dedupe_hits(hits)] == ["h1", "h3"]
    assert dedupe_hits([]) == []


def test_dedupe_limits_hits_per_source_and_keeps_order():
    hits = [hit(1, "a.md"), hit(2, "a.md"), hit(3, "b.md"), hit(4, "a.md"), hit(5, "b.md")]
    assert [h["id"] for h in dedupe_hits(hits, max_per_source=2)] == ["h1", "h2", "h3", "h5"]
    assert len(dedupe_hits(hits)) == 5, "no limit by default"


def test_dedupe_does_not_count_dropped_repeats_against_the_limit():
    hits = [hit(1, "a.md", "same"), hit(2, "a.md", "same"), hit(3, "a.md", "new")]
    assert [h["id"] for h in dedupe_hits(hits, max_per_source=2)] == ["h1", "h3"]


def test_prepare_context_puts_the_best_at_the_edges():
    hits = [hit(i, source=f"s{i}.md") for i in range(1, 6)]
    assert [h["id"] for h in prepare_context(hits, 5)] == ["h1", "h3", "h5", "h4", "h2"]
    assert [h["id"] for h in prepare_context(hits, 4)] == ["h1", "h3", "h4", "h2"]
    assert [h["id"] for h in prepare_context(hits, 2)] == ["h1", "h2"]
    assert prepare_context(hits, 0) == []


def test_prepare_context_dedupes_before_cutting():
    hits = [hit(1, "a.md", "same"), hit(2, "b.md", "same"), hit(3, "c.md"), hit(4, "d.md")]
    assert [h["id"] for h in prepare_context(hits, 3)] == ["h1", "h4", "h3"]


def test_prepare_context_limits_one_source():
    hits = [hit(i, "a.md") for i in range(1, 6)] + [hit(9, "b.md")]
    ids = [h["id"] for h in prepare_context(hits, 4, max_per_source=2)]
    assert sorted(ids) == ["h1", "h2", "h9"]


def test_classify_failure():
    assert classify_failure(["c1"], ["c9", "c1"], True) == "ok"
    assert classify_failure(["c1"], ["c9"], True) == "retrieval_miss", "the chunk never arrived"
    assert classify_failure(["c1"], ["c1"], False) == "generation_miss", "the chunk arrived but the answer is bad"
    assert classify_failure([], ["c9"], True) == "ok", "no answer in the docs, and the model said so"
    assert classify_failure([], ["c9"], False) == "hallucination"
    assert classify_failure(["c1", "c2"], ["c2"], True) == "ok", "any expected chunk is enough"


def test_failure_report():
    results = [
        {"question": "q1", "expected": ["a"], "retrieved": ["a"], "answer_ok": True},
        {"question": "q2", "expected": ["a"], "retrieved": ["b"], "answer_ok": False},
        {"question": "q3", "expected": ["a"], "retrieved": ["a"], "answer_ok": False},
        {"question": "q4", "expected": [], "retrieved": ["a"], "answer_ok": False},
        {"question": "q5", "expected": ["a"], "retrieved": ["b"], "answer_ok": True},
    ]
    report = failure_report(results)
    assert report["counts"] == {"ok": 1, "retrieval_miss": 2, "generation_miss": 1, "hallucination": 1}
    assert report["by_category"]["retrieval_miss"] == ["q2", "q5"]
    assert list(report["counts"]) == CATEGORIES
    assert failure_report([])["counts"] == {name: 0 for name in CATEGORIES}


def test_retrieve_prepared_and_answer_prepared():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    chunks = [
        {"id": "a:0", "source": "a.md", "heading": "A", "text": "task one"},
        {"id": "a:1", "source": "a.md", "heading": "B", "text": "task two"},
        {"id": "a:2", "source": "a.md", "heading": "C", "text": "task three"},
        {"id": "b:0", "source": "b.md", "heading": "D", "text": "login four"},
    ]
    add_chunks(collection, chunks, embed=embed)
    hits = retrieve_prepared(collection, "task", k=4, pool=4, max_per_source=2, embed=embed)
    assert sum(1 for h in hits if h["source"] == "a.md") == 2, "at most 2 chunks per source"
    client = FakeClient("Yes [1].")
    result = answer_prepared(client, collection, "task", k=4, pool=4, embed=embed)
    assert result["ok"] and len(client.calls) == 1
