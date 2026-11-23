"""Step 23 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.guardrails import check_input
from copilot.store import add_chunks, open_collection
from copilot.tracing import (
    add_span,
    find_regressions,
    gate,
    pass_rate,
    percentile,
    run_eval,
    trace_summary,
    traced_call,
    traced_rag,
    trajectory_match,
)


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id")]


class Clock:
    def __init__(self, step=0.05):
        self.t = 0.0
        self.step = step

    def __call__(self):
        self.t += self.step
        return self.t


class FakeClient:
    def __init__(self, text="Use DELETE [1].", total_tokens=120, with_usage=True):
        self.text, self.total_tokens, self.with_usage = text, total_tokens, with_usage
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        response = NS(choices=[NS(message=NS(content=self.text))])
        if self.with_usage:
            response.usage = NS(total_tokens=self.total_tokens)
        return response


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    assert check_input("hello")["ok"] is True


def test_add_span_and_summary():
    trace = []
    add_span(trace, "search", "tool", 1.0, 1.25)
    add_span(trace, "model", "llm", 2.0, 3.0, tokens=100)
    add_span(trace, "bad", "tool", 4.0, 4.1, error="boom")
    assert trace[0] == {"name": "search", "kind": "tool", "ms": 250}
    assert trace_summary(trace) == {"spans": 3, "total_ms": 1350, "llm_calls": 1, "tool_calls": 2, "tokens": 100, "errors": 1}


def test_traced_call_records_success_and_failure():
    trace = []
    assert traced_call(trace, "add", "tool", Clock(), lambda a, b: a + b, 2, b=3) == 5
    assert trace == [{"name": "add", "kind": "tool", "ms": 50}]

    def broken():
        raise ValueError("nope")

    try:
        traced_call(trace, "broken", "tool", Clock(), broken)
        raise AssertionError("the error must be raised again")
    except ValueError:
        pass
    assert trace[-1] == {"name": "broken", "kind": "tool", "ms": 50, "error": "nope"}


def test_traced_rag_has_a_tool_span_and_an_llm_span_with_tokens():
    out = traced_rag(FakeClient(), filled(), "how do I delete a task", clock=Clock(), embed=embed)
    assert out["answer"] == "Use DELETE [1]." and out["hits"][0]["id"] == "tasks.md:0"
    assert [(s["name"], s["kind"]) for s in out["trace"]] == [("retrieve", "tool"), ("answer", "llm")]
    assert out["trace"][1]["tokens"] == 120
    assert trace_summary(out["trace"])["tokens"] == 120


def test_missing_usage_counts_as_zero_tokens():
    out = traced_rag(FakeClient(with_usage=False), filled(), "delete a task", clock=Clock(), embed=embed)
    assert out["trace"][1]["tokens"] == 0


def test_trajectory_modes():
    assert trajectory_match(["a", "b"], ["a", "b"], "exact") is True
    assert trajectory_match(["a", "x", "b"], ["a", "b"], "exact") is False
    assert trajectory_match(["a", "x", "b"], ["a", "b"], "in_order") is True
    assert trajectory_match(["b", "a"], ["a", "b"], "in_order") is False
    assert trajectory_match(["b", "a"], ["a", "b"], "any_order") is True


def agent_for(table):
    def agent(question):
        if question == "crash":
            raise RuntimeError("model down")
        return table[question]

    return agent


def test_run_eval_checks_answer_and_trajectory_and_survives_a_crash():
    good = {"answer": "Use DELETE", "trace": [{"name": "retrieve", "kind": "tool", "ms": 10, "tokens": 0},
                                            {"name": "answer", "kind": "llm", "ms": 90, "tokens": 50}]}
    wrong_tool = {"answer": "Use DELETE", "trace": [{"name": "other", "kind": "tool", "ms": 5}]}
    cases = [
        {"id": "a", "input": "q1", "must_contain": ["delete"], "expected_tools": ["retrieve"]},
        {"id": "b", "input": "q2", "must_contain": ["delete"], "expected_tools": ["retrieve"]},
        {"id": "c", "input": "q3", "must_contain": ["missing"], "expected_tools": []},
        {"id": "d", "input": "crash"},
    ]
    results = run_eval(agent_for({"q1": good, "q2": wrong_tool, "q3": good}), cases)
    assert [r["passed"] for r in results] == [True, False, False, False]
    assert results[0] == {"id": "a", "answer_ok": True, "trajectory_ok": True, "passed": True,
                          "steps": 1, "tokens": 50, "ms": 100}
    assert results[1]["answer_ok"] is True and results[1]["trajectory_ok"] is False
    assert results[3]["error"] == "model down"
    assert pass_rate(results) == 0.25


def r(id, passed, tokens=100):
    return {"id": id, "passed": passed, "tokens": tokens}


def test_gate_blocks_a_worse_run():
    baseline = [r("a", True), r("b", True), r("c", False), r("d", True)]
    assert find_regressions(baseline, [r("a", True), r("b", False), r("c", True), r("d", True)]) == ["b"]
    same = gate(baseline, [r("a", True), r("b", True), r("c", False), r("d", True)])
    assert same == {"ok": True, "reasons": []}
    worse = gate(baseline, [r("a", True), r("b", False), r("c", False), r("d", True)])
    assert worse["ok"] is False
    assert worse["reasons"] == ["pass rate fell by 0.25", "regressions: b"]
    costly = gate([r("a", True, 100)], [r("a", True, 150)])
    assert costly == {"ok": False, "reasons": ["token use grew by 50%"]}


def test_percentile():
    assert percentile(list(range(1, 101)), 95) == 95
    assert percentile([], 95) == 0
