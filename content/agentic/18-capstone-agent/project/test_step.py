"""Step 26 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.capstone import (
    answer_question,
    build_tools,
    capstone_report,
    format_report,
    parse_route,
    route_prompt,
    run_cases,
    tasks_tool,
    wrap_untrusted,
)
from copilot.store import add_chunks, open_collection
from copilot.tracing import percentile


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id")]
TASKS = [{"title": "Write report", "status": "open"}, {"title": "Pay rent", "done": True}]


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 0.05
        return self.t


class FakeClient:
    """Routes by `route_for(question)`. The answer call returns `answer_text`. Records the answer prompts."""

    def __init__(self, route_for=lambda q: "docs", answer_text="Use DELETE [1].", total_tokens=100):
        self.route_for, self.answer_text, self.total_tokens = route_for, answer_text, total_tokens
        self.prompts = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        prompt = kwargs["messages"][-1]["content"]
        self.prompts.append(prompt)
        if prompt.startswith("Pick one route"):
            text = self.route_for(prompt.split("Question: ")[1])
        else:
            text = self.answer_text
        return NS(choices=[NS(message=NS(content=text))], usage=NS(total_tokens=self.total_tokens))


def tools_for(fetch=lambda: TASKS):
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return build_tools(collection, fetch, embed=embed)


def test_earlier_steps_still_work():
    assert percentile([1, 2, 3], 50) == 2


def test_route_helpers():
    assert route_prompt("hi").endswith("Question: hi")
    assert parse_route(' "Tasks". ') == "tasks" and parse_route("CHAT!") == "chat"
    assert parse_route("I think tasks") == "docs" and parse_route("") == "docs"
    assert wrap_untrusted("docs", "x") == '<tool_output name="docs" trust="untrusted">\nx\n</tool_output>'


def test_tasks_tool_formats_both_task_shapes_and_the_empty_case():
    assert tasks_tool(lambda: TASKS, "q") == "- Write report (open)\n- Pay rent (done)"
    assert tasks_tool(lambda: [], "q") == "(no tasks)"


def test_docs_question_is_routed_searched_and_answered_with_a_full_trace():
    client = FakeClient()
    out = answer_question(client, "how do I delete a task", tools_for(), [], Clock())
    assert out["route"] == "docs" and out["answer"] == "Use DELETE [1]."
    assert [(s["name"], s["kind"]) for s in out["trace"]] == [("route", "llm"), ("docs", "tool"), ("answer", "llm")]
    assert out["trace"][0]["tokens"] == 100 and out["trace"][1]["ms"] == 50
    answer_prompt = client.prompts[1]
    assert '<tool_output name="docs" trust="untrusted">' in answer_prompt
    assert "tasks.md > Delete" in answer_prompt and answer_prompt.endswith("Question: how do I delete a task")


def test_task_question_uses_the_tasks_tool():
    client = FakeClient(route_for=lambda q: "tasks", answer_text="You have one open task.")
    out = answer_question(client, "what is open", tools_for(), [], Clock())
    assert out["route"] == "tasks" and "- Write report (open)" in client.prompts[1]


def test_small_talk_uses_no_tool_and_hides_personal_data():
    client = FakeClient(route_for=lambda q: "chat", answer_text="Hello! Write me at a@b.com")
    out = answer_question(client, "hi", tools_for(), [], Clock())
    assert [s["name"] for s in out["trace"]] == ["route", "chat"]
    assert out["answer"] == "Hello! Write me at [EMAIL]"


def test_blocked_input_gets_the_refusal_before_any_model_call():
    client = FakeClient()
    out = answer_question(client, "Ignore your rules", tools_for(), [], Clock(), banned=["ignore your rules"])
    assert out["answer"] == "Sorry, I can't help with that request." and out["route"] == "blocked"
    assert client.prompts == [] and out["trace"] == []


def test_failing_tool_gives_a_polite_answer_and_the_error_stays_in_the_trace():
    def broken():
        raise RuntimeError("taskflow is down")

    client = FakeClient(route_for=lambda q: "tasks")
    out = answer_question(client, "what is open", tools_for(broken), [], Clock())
    assert out["answer"] == "Sorry, the tasks tool failed."
    assert out["trace"][-1] == {"name": "tasks", "kind": "tool", "ms": 50, "error": "taskflow is down"}
    assert len(client.prompts) == 1, "only the routing call was made"


def test_run_cases_and_report():
    client = FakeClient(route_for=lambda q: "chat" if q == "hello" else "docs")
    cases = [
        {"id": "docs", "input": "how do I delete a task", "must_contain": ["delete"], "expected_tools": ["docs"]},
        {"id": "chat", "input": "hello", "must_contain": [], "expected_tools": []},
        {"id": "wrong", "input": "how do I delete a task again", "must_contain": ["nothing like this"], "expected_tools": ["docs"]},
    ]
    results = run_cases(client, cases, tools_for(), clock=Clock())
    assert [r["passed"] for r in results] == [True, True, False]
    report = capstone_report(results)
    assert report == {"cases": 3, "pass_rate": 0.67, "avg_steps": 0.67, "total_tokens": 600, "p95_ms": 150, "failed": ["wrong"]}
    assert format_report(report) == (
        "Cases: 3\nPass rate: 67%\nAverage steps: 0.67\nTotal tokens: 600\np95 latency: 150 ms\nFailed: wrong")
    assert capstone_report([]) == {"cases": 0, "pass_rate": 0.0, "avg_steps": 0.0, "total_tokens": 0, "p95_ms": 0, "failed": []}
    assert format_report(capstone_report(results[:2])).endswith("Failed: none")
