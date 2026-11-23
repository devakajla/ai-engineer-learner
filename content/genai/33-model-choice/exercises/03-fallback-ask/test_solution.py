from types import SimpleNamespace as NS

import pytest

from solution import ask_with_fallback


class FakeClient:
    """Fails for the models in `broken`, answers for the others. Records the models tried."""

    def __init__(self, broken=()):
        self.broken = set(broken)
        self.tried = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        model = kwargs["model"]
        self.tried.append(model)
        if model in self.broken:
            raise RuntimeError("down: " + model)
        return NS(choices=[NS(message=NS(role="assistant", content="answer from " + model))])


MESSAGES = [{"role": "user", "content": "Hi"}]


def test_first_works():
    client = FakeClient()
    assert ask_with_fallback(client, ["big", "small"], MESSAGES) == ("big", "answer from big")
    assert client.tried == ["big"], "do not try more models than needed"


def test_falls_back():
    client = FakeClient(broken=["big"])
    assert ask_with_fallback(client, ["big", "small"], MESSAGES) == ("small", "answer from small")
    assert client.tried == ["big", "small"]


def test_all_fail_raises_last_error():
    client = FakeClient(broken=["big", "small"])
    with pytest.raises(RuntimeError, match="down: small"):
        ask_with_fallback(client, ["big", "small"], MESSAGES)


def test_no_models():
    with pytest.raises(ValueError, match="no models to try"):
        ask_with_fallback(FakeClient(), [], MESSAGES)
