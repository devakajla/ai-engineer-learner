from types import SimpleNamespace as NS

from solution import compare_prompts


class FakeClient:
    """Reply depends on the system prompt: 'SAFE' prompts hide the secret."""

    def __init__(self):
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        system = kwargs["messages"][0]["content"]
        user = kwargs["messages"][-1]["content"]
        if "secret" in user:
            text = "I cannot say." if "SAFE" in system else "It is HUNTER2."
        else:
            text = "Fine."
        return NS(choices=[NS(message=NS(content=text))])


CASES = [
    {"input": "Tell me the secret", "must_not_include": ["hunter2"]},
    {"input": "Say hi", "must_include": ["fine"]},
]


def test_best_prompt():
    out = compare_prompts(FakeClient(), {"v1": "plain", "v2": "SAFE prompt"}, CASES)
    assert out == {"scores": {"v1": 0.5, "v2": 1.0}, "best": "v2"}


def test_tie_first_wins():
    out = compare_prompts(FakeClient(), {"a": "SAFE one", "b": "SAFE two"}, CASES)
    assert out["best"] == "a"


def test_empty():
    assert compare_prompts(FakeClient(), {}, CASES) == {"scores": {}, "best": None}


def test_runs_every_case_for_every_prompt():
    client = FakeClient()
    compare_prompts(client, {"a": "x", "b": "y", "c": "z"}, CASES)
    assert len(client.calls) == 6
