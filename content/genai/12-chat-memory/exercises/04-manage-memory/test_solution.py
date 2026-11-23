from types import SimpleNamespace as NS

from solution import manage_memory


class FakeClient:
    def __init__(self, summary="They talked about Python."):
        self.summary = summary
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.summary))])


def msg(role, text):
    return {"role": role, "content": text}


SHORT = [msg("user", "hi"), msg("assistant", "hello")]
LONG = [msg("user", "a" * 200), msg("assistant", "b" * 200), msg("user", "c" * 40), msg("assistant", "d" * 40)]


def test_short_history_no_call():
    client = FakeClient()
    out = manage_memory(client, SHORT, keep_last=1, max_tokens=1000)
    assert out == SHORT and out is not SHORT, "return a copy"
    assert client.calls == [], "no model call when the history fits"


def test_long_history_is_summarized_and_fits():
    client = FakeClient()
    out = manage_memory(client, LONG, keep_last=2, max_tokens=60)
    assert len(client.calls) == 1
    assert out[0]["content"].startswith("Summary of the earlier chat:")
    assert out[-2:] == LONG[-2:], "recent messages are kept"
    total = sum((len(m["content"]) + 3) // 4 for m in out)
    assert total <= 60, "the result must fit the budget"


def test_trims_when_summary_is_still_too_big():
    client = FakeClient(summary="x" * 400)
    out = manage_memory(client, LONG, keep_last=2, max_tokens=30)
    total = sum((len(m["content"]) + 3) // 4 for m in out)
    assert total <= 30
    assert out == LONG[-2:] or out[-1] == LONG[-1]


def test_empty_history():
    client = FakeClient()
    assert manage_memory(client, [], 2, 10) == []
    assert client.calls == []
