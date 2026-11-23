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

from solution import supervise


def test_runs_workers_in_the_order_the_supervisor_picks():
    client = FnClient(script(["researcher", "writer", "FINISH"]))
    out = supervise(client, WORKERS, "Explain RAG")
    assert [r["worker"] for r in out["results"]] == ["researcher", "writer"]
    assert out["steps"] == 2 and out["finished"] is True


def test_each_worker_sees_the_work_so_far():
    client = FnClient(script(["researcher", "writer", "FINISH"]))
    supervise(client, WORKERS, "Explain RAG")
    worker_calls = [c for c in client.calls if c["system"]]
    assert worker_calls[0]["prompt"] == "Explain RAG"
    assert worker_calls[1]["prompt"] == "Explain RAG\n\nWork so far:\nresearcher: researcher done"


def test_finish_straight_away_runs_no_worker():
    out = supervise(FnClient(script(["FINISH"])), WORKERS, "Hi")
    assert out == {"results": [], "steps": 0, "finished": True}


def test_max_steps_stops_a_supervisor_that_never_finishes():
    client = FnClient(script(["researcher"] * 10))
    out = supervise(client, WORKERS, "T", max_steps=3)
    assert out["steps"] == 3 and out["finished"] is False
    assert len([c for c in client.calls if c["system"] is None]) == 3, "one supervisor call per step"


def test_unknown_worker_name_stops_the_loop():
    out = supervise(FnClient(script(["researcher", "the intern"])), WORKERS, "T")
    assert out["steps"] == 1 and out["finished"] is False
