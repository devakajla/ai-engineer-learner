from types import SimpleNamespace as NS

import pytest

from solution import Ticket, ask_ticket


class FakeClient:
    """Returns the given replies one by one, and keeps a copy of the messages of each call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        text = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return NS(choices=[NS(message=NS(role="assistant", content=text))])


GOOD = '{"title": "Login crash", "priority": 5}'
BAD = '{"title": "Login crash", "priority": 9}'


def test_valid_first_time():
    client = FakeClient([GOOD])
    ticket = ask_ticket(client, "Login page crashes")
    assert isinstance(ticket, Ticket) and ticket.priority == 5
    assert len(client.calls) == 1, "do not call again after a good reply"
    call = client.calls[0]
    assert call["response_format"] == {"type": "json_object"}
    assert call["messages"][0]["role"] == "system"
    assert call["messages"][1] == {"role": "user", "content": "Login page crashes"}


def test_repairs_a_bad_reply():
    client = FakeClient([BAD, GOOD])
    ticket = ask_ticket(client, "Login page crashes")
    assert ticket.priority == 5
    assert len(client.calls) == 2
    second = client.calls[1]["messages"]
    assert second[-2] == {"role": "assistant", "content": BAD}, "send the bad reply back"
    assert second[-1]["role"] == "user"
    assert "Your reply was invalid:" in second[-1]["content"], "tell the model what was wrong"
    assert "priority" in second[-1]["content"], "the error text names the bad field"
    assert len(client.calls[0]["messages"]) == 2, "the first call must keep only its own 2 messages"


def test_gives_up():
    client = FakeClient([BAD])
    with pytest.raises(ValueError, match="could not get a valid ticket"):
        ask_ticket(client, "x", max_tries=2)
    assert len(client.calls) == 2


def test_not_json_is_also_repaired():
    client = FakeClient(["Sure, here you go!", GOOD])
    assert ask_ticket(client, "x").title == "Login crash"
