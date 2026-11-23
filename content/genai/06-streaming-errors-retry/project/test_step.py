"""Step 3 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

import groq
import httpx
import pytest

from copilot import cli
from copilot.llm import DEFAULT_MODEL, ask, backoff_delays, chat_turn, complete_with_retry, stream_answer

MESSAGES = [{"role": "user", "content": "Hi"}]


def connection_error():
    return groq.APIConnectionError(request=httpx.Request("POST", "https://api.groq.com/test"))


class FakeClient:
    """Raises the given errors first (one per call), then answers."""

    def __init__(self, errors=(), text="Hello!", pieces=None):
        self.errors = list(errors)
        self.text = text
        self.pieces = pieces
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({"model": kwargs["model"], "messages": list(kwargs["messages"]), "stream": kwargs.get("stream", False)})
        if self.errors:
            raise self.errors.pop(0)
        if kwargs.get("stream"):
            return [NS(choices=[NS(delta=NS(content=p))]) for p in self.pieces]
        return NS(choices=[NS(message=NS(role="assistant", content=self.text), finish_reason="stop")])


def test_earlier_steps_still_work():
    client = FakeClient(text="Hi!")
    assert ask(client, "Hello") == "Hi!"
    reply, history = chat_turn(client, [], "Hello")
    assert reply == "Hi!" and len(history) == 2


def test_backoff_delays():
    assert backoff_delays(4) == [1, 2, 4, 8]
    assert backoff_delays(6, base=1, cap=10) == [1, 2, 4, 8, 10, 10]
    assert backoff_delays(0) == []


def test_retries_a_flaky_call():
    client = FakeClient(errors=[connection_error(), connection_error()])
    assert complete_with_retry(client, MESSAGES, base_delay=0) == "Hello!"
    assert len(client.calls) == 3, "two failures, then a success: 3 calls in total"


def test_gives_up_after_max_tries():
    client = FakeClient(errors=[connection_error() for _ in range(5)])
    with pytest.raises(groq.APIConnectionError):
        complete_with_retry(client, MESSAGES, max_tries=3, base_delay=0)
    assert len(client.calls) == 3, "stop after max_tries calls"


def test_other_errors_are_not_retried():
    client = FakeClient(errors=[RuntimeError("bug"), RuntimeError("bug")])
    with pytest.raises(RuntimeError):
        complete_with_retry(client, MESSAGES, base_delay=0)
    assert len(client.calls) == 1, "only retry errors that can go away (RETRYABLE), not every error"


def test_max_tries_must_be_positive():
    with pytest.raises(ValueError):
        complete_with_retry(FakeClient(), MESSAGES, max_tries=0)


def test_stream_answer_joins_pieces():
    client = FakeClient(pieces=["Hel", None, "lo"])
    assert stream_answer(client, MESSAGES) == "Hello"
    assert client.calls[0]["stream"] is True, "pass stream=True"


def test_chat_turn_retries():
    client = FakeClient(errors=[connection_error()], text="Back again")
    reply, history = chat_turn(client, [], "Hi", base_delay=0)
    assert reply == "Back again"
    assert len(client.calls) == 2
    assert client.calls[0]["model"] == DEFAULT_MODEL


def test_cli_chat_runs(monkeypatch, capsys):
    client = FakeClient(text="Hello from the fake model")
    monkeypatch.setattr(cli, "get_client", lambda: client)
    typed = iter(["hi", "", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(typed))
    cli.main()
    out = capsys.readouterr().out
    assert "Copilot: Hello from the fake model" in out
    assert len(client.calls) == 1, "an empty line must not call the model"


def test_cli_survives_an_error(monkeypatch, capsys):
    client = FakeClient(errors=[RuntimeError("boom")], text="second answer")
    monkeypatch.setattr(cli, "get_client", lambda: client)
    typed = iter(["one", "two", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(typed))
    cli.main()
    out = capsys.readouterr().out
    assert "Sorry" in out, "print a friendly message when a call fails"
    assert "Copilot: second answer" in out, "the chat must continue after an error"
