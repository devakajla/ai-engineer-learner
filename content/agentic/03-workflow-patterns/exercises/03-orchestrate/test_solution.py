from types import SimpleNamespace as NS


class FakeClient:
    """Returns the replies one by one (the last one repeats). Records every call."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.replies) - 1)
        return NS(choices=[NS(message=NS(content=self.replies[index]))])


def user_text(call):
    return call["messages"][-1]["content"]


def system_text(call):
    first = call["messages"][0]
    return first["content"] if first["role"] == "system" else None

from solution import orchestrate


def test_plan_workers_and_combine():
    client = FakeClient("- boil water\n- steep the leaves\n\n- add milk", "w1", "w2", "w3", "final guide")
    out = orchestrate(client, "Make tea")
    assert out == {
        "subtasks": ["boil water", "steep the leaves", "add milk"],
        "results": ["w1", "w2", "w3"],
        "answer": "final guide",
    }
    assert len(client.calls) == 5


def test_plan_prompt():
    client = FakeClient("only one", "w", "f")
    orchestrate(client, "Make tea", max_subtasks=2)
    assert user_text(client.calls[0]) == (
        "Split this task into at most 2 short subtasks, one per line, no numbering:\nMake tea"
    )


def test_worker_prompts():
    client = FakeClient("a\nb", "wa", "wb", "done")
    orchestrate(client, "T")
    assert user_text(client.calls[1]) == "Task: T\nSubtask: a\nDo only this subtask."
    assert user_text(client.calls[2]) == "Task: T\nSubtask: b\nDo only this subtask."


def test_combine_prompt():
    client = FakeClient("a\nb", "wa", "wb", "done")
    orchestrate(client, "T")
    assert user_text(client.calls[3]) == (
        "Combine these results into one answer for the task.\n\nTask: T\n\nResults:\n1. wa\n2. wb"
    )


def test_more_subtasks_than_the_limit_are_dropped():
    client = FakeClient("a\nb\nc\nd", "x", "x", "final")
    out = orchestrate(client, "T", max_subtasks=2)
    assert out["subtasks"] == ["a", "b"] and len(client.calls) == 4


def test_bullet_characters_are_removed():
    client = FakeClient("* one\n\u2022 two\n-  three", "x", "x", "x", "final")
    assert orchestrate(client, "T")["subtasks"] == ["one", "two", "three"]


def test_no_subtasks_means_a_direct_answer():
    client = FakeClient("  \n\n", "direct answer")
    out = orchestrate(client, "T")
    assert out == {"subtasks": [], "results": [], "answer": "direct answer"}
    assert len(client.calls) == 2 and user_text(client.calls[1]) == "T"
