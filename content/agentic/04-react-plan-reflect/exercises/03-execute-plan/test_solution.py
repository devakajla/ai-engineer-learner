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


from solution import execute_plan


def user_text(call):
    return call["messages"][-1]["content"]


def test_runs_every_step_and_collects_results():
    client = FakeClient("r1", " r2 ", "r3")
    out = execute_plan(client, "G", ["a", "b", "c"])
    assert out == {"results": ["r1", "r2", "r3"], "steps_run": 3, "skipped": 0}
    assert len(client.calls) == 3


def test_each_call_sees_the_earlier_results():
    client = FakeClient("r1", "r2")
    execute_plan(client, "G", ["a", "b"])
    assert "Results so far:\n(none yet)" in user_text(client.calls[0])
    assert "Results so far:\n1. r1" in user_text(client.calls[1])
    assert "Current step (2 of 2): b" in user_text(client.calls[1])


def test_limit_skips_the_rest_but_the_plan_stays_whole():
    client = FakeClient("r1", "r2")
    out = execute_plan(client, "G", ["a", "b", "c", "d"], max_steps=2)
    assert out == {"results": ["r1", "r2"], "steps_run": 2, "skipped": 2}
    assert len(client.calls) == 2
    assert "Current step (2 of 4): b" in user_text(client.calls[1]), "the whole plan is shown, with 4 steps"


def test_empty_plan_makes_no_call():
    client = FakeClient("never")
    assert execute_plan(client, "G", []) == {"results": [], "steps_run": 0, "skipped": 0}
    assert client.calls == []


def test_call_settings():
    client = FakeClient("r")
    execute_plan(client, "G", ["a"])
    assert client.calls[0]["temperature"] == 0
    assert client.calls[0]["messages"][0]["role"] == "system"


def test_default_limit_is_eight():
    client = FakeClient("r")
    out = execute_plan(client, "G", [str(n) for n in range(10)])
    assert out["steps_run"] == 8 and out["skipped"] == 2
