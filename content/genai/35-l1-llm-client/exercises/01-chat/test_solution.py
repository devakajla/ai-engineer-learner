from types import SimpleNamespace as NS

import pytest

from solution import chat


class FakeClient:
    def __init__(self, fail_times=0, text="Hello!"):
        self.fail_times = fail_times
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        if len(self.calls) <= self.fail_times:
            raise RuntimeError(f"fail #{len(self.calls)}")
        return NS(choices=[NS(message=NS(role="assistant", content=self.text), finish_reason="stop")])


def test_first_turn_and_settings():
    client = FakeClient()
    reply, history = chat(client, [], "Hi")
    assert reply == "Hello!"
    assert history == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    call = client.calls[0]
    assert call["model"] == "qwen/qwen3.8-27b"
    assert call["temperature"] == 0.7 and call["max_completion_tokens"] == 500, "use the chat settings"


def test_task_changes_settings():
    client = FakeClient()
    chat(client, [], "Pull the date out.", task="extract")
    assert client.calls[0]["temperature"] == 0
    assert client.calls[0]["max_completion_tokens"] == 200


def test_history_is_sent_and_not_changed():
    client = FakeClient()
    old = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
    _, new = chat(client, old, "c")
    assert [m["content"] for m in client.calls[0]["messages"]] == ["a", "b", "c"]
    assert len(old) == 2, "do not change the history that was passed in"
    assert len(new) == 4


def test_unknown_task_fails_before_any_call():
    client = FakeClient()
    with pytest.raises(ValueError, match="unknown task: poem"):
        chat(client, [], "Hi", task="poem")
    assert client.calls == [], "no call may be made for a bad task"


def test_retries_with_backoff():
    waits = []
    client = FakeClient(fail_times=2)
    reply, _ = chat(client, [], "Hi", max_tries=4, sleep=waits.append)
    assert reply == "Hello!"
    assert len(client.calls) == 3
    assert waits == [1, 2]


def test_all_fail():
    waits = []
    client = FakeClient(fail_times=10)
    with pytest.raises(RuntimeError, match="fail #3"):
        chat(client, [], "Hi", max_tries=3, sleep=waits.append)
    assert waits == [1, 2], "no wait after the last failed try"


def test_max_tries_must_be_positive():
    with pytest.raises(ValueError, match="max_tries must be at least 1"):
        chat(FakeClient(), [], "Hi", max_tries=0)
