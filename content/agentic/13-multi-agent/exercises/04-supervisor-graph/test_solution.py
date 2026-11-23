from types import SimpleNamespace as NS


class FnClient:
    """A fake model. fn(prompt, system) gives the reply. Records every call."""

    def __init__(self, fn):
        self.fn = fn
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        messages = kwargs["messages"]
        system = messages[0]["content"] if messages[0]["role"] == "system" else None
        prompt = messages[-1]["content"]
        self.calls.append({"system": system, "prompt": prompt})
        return NS(choices=[NS(message=NS(content=self.fn(prompt, system)))])


WORKERS = {
    "researcher": {"description": "finds facts", "system": "You are a researcher."},
    "writer": {"description": "writes the final text", "system": "You are a writer."},
}


def script(choices):
    """fn for a supervisor that picks the given choices in order, and workers that echo their name."""
    items = list(choices)

    def fn(prompt, system):
        if system is None:
            return items.pop(0) if items else "FINISH"
        return system.split()[-1].strip(".") + " done"

    return fn

from solution import build_handoff_graph, build_supervisor_graph


def start(task="Explain RAG"):
    return {"task": task, "results": [], "next": ""}


def test_graph_runs_workers_then_finishes():
    app = build_supervisor_graph(FnClient(script(["researcher", "writer", "FINISH"])), WORKERS)
    out = app.invoke(start())
    assert [r["worker"] for r in out["results"]] == ["researcher", "writer"]
    assert out["next"] == "FINISH"


def test_stream_shows_the_supervisor_between_workers():
    app = build_supervisor_graph(FnClient(script(["researcher", "writer", "FINISH"])), WORKERS)
    names = [list(u)[0] for u in app.stream(start(), stream_mode="updates")]
    assert names == ["supervisor", "researcher", "supervisor", "writer", "supervisor"]


def test_worker_sees_earlier_results():
    client = FnClient(script(["researcher", "writer", "FINISH"]))
    build_supervisor_graph(client, WORKERS).invoke(start())
    worker_calls = [c for c in client.calls if c["system"]]
    assert worker_calls[1]["prompt"].endswith("Work so far:\nresearcher: researcher done")


def test_max_steps_and_unknown_choice_both_end_the_graph():
    app = build_supervisor_graph(FnClient(script(["researcher"] * 9)), WORKERS, max_steps=2)
    assert len(app.invoke(start())["results"]) == 2
    app = build_supervisor_graph(FnClient(script(["the intern"])), WORKERS)
    assert app.invoke(start())["results"] == []


def test_workers_dict_decides_the_nodes():
    one = {"researcher": WORKERS["researcher"]}
    app = build_supervisor_graph(FnClient(script(["researcher", "FINISH"])), one)
    assert len(app.invoke(start())["results"]) == 1


def test_handoff_graph_passes_control_with_command():
    app = build_handoff_graph()
    out = app.invoke({"topic": "RAG", "notes": "", "draft": ""})
    assert out == {"topic": "RAG", "notes": "facts about RAG", "draft": "Report: facts about RAG"}
    names = [list(u)[0] for u in app.stream({"topic": "RAG", "notes": "", "draft": ""}, stream_mode="updates")]
    assert names == ["researcher", "writer"]
