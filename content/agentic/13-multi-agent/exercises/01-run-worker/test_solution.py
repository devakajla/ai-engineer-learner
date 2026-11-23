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

from solution import format_results, run_worker


def test_worker_uses_its_system_prompt_and_returns_name_and_output():
    client = FnClient(lambda p, s: "3 facts")
    out = run_worker(client, "researcher", WORKERS["researcher"], "Explain RAG")
    assert out == {"worker": "researcher", "output": "3 facts"}
    assert client.calls == [{"system": "You are a researcher.", "prompt": "Explain RAG"}]


def test_context_is_added_after_the_task():
    client = FnClient(lambda p, s: "ok")
    run_worker(client, "writer", WORKERS["writer"], "Explain RAG", context="researcher: 3 facts")
    assert client.calls[0]["prompt"] == "Explain RAG\n\nWork so far:\nresearcher: 3 facts"


def test_empty_context_adds_nothing():
    client = FnClient(lambda p, s: "ok")
    run_worker(client, "writer", WORKERS["writer"], "T", context="")
    assert client.calls[0]["prompt"] == "T"


def test_format_results_one_line_per_result():
    results = [{"worker": "a", "output": "one"}, {"worker": "b", "output": "two"}]
    assert format_results(results) == "a: one\nb: two"
    assert format_results([]) == ""
