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

from solution import parse_choice, supervisor_prompt

NAMES = ["researcher", "writer"]


def test_prompt_lists_workers_and_work_so_far():
    results = [{"worker": "researcher", "output": "3 facts"}]
    assert supervisor_prompt("Explain RAG", WORKERS, results) == (
        "Task: Explain RAG\n\n"
        "Workers:\n- researcher: finds facts\n- writer: writes the final text\n\n"
        "Work so far:\nresearcher: 3 facts\n\n"
        "Which worker should act next? Reply with one worker name, or FINISH if the task is done."
    )


def test_prompt_with_no_results_says_nothing_yet():
    prompt = supervisor_prompt("T", WORKERS, [])
    assert "Work so far:\n(nothing yet)\n\n" in prompt


def test_parse_choice_exact_names():
    assert parse_choice("researcher", NAMES) == "researcher"
    assert parse_choice("writer", NAMES) == "writer"
    assert parse_choice("FINISH", NAMES) == "FINISH"


def test_parse_choice_ignores_case_spaces_and_punctuation():
    assert parse_choice("  Writer. ", NAMES) == "writer"
    assert parse_choice('"researcher"', NAMES) == "researcher"
    assert parse_choice("finish!", NAMES) == "FINISH"


def test_parse_choice_returns_none_for_anything_else():
    assert parse_choice("the researcher please", NAMES) is None
    assert parse_choice("banana", NAMES) is None
    assert parse_choice("", NAMES) is None
