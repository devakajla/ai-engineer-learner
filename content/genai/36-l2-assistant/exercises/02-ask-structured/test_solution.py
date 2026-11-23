from types import SimpleNamespace as NS

import pytest
from pydantic import BaseModel

from solution import Ticket, ask_structured


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        text = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return NS(choices=[NS(message=NS(role="assistant", content=text))])


class Mood(BaseModel):
    mood: str


MSGS = [{"role": "user", "content": "hi"}]
GOOD = '{"title": "x", "priority": 4}'
BAD = '{"title": "x", "priority": 9}'


def test_good_first_time():
    client = FakeClient([GOOD])
    result = ask_structured(client, MSGS, Ticket)
    assert result.priority == 4 and len(client.calls) == 1
    call = client.calls[0]
    assert call["response_format"] == {"type": "json_object"}
    assert call["temperature"] == 0
    assert call["model"] == "qwen/qwen3.8-27b"


def test_works_with_another_model():
    client = FakeClient(['{"mood": "happy"}'])
    assert ask_structured(client, MSGS, Mood).mood == "happy"


def test_repairs():
    client = FakeClient([BAD, GOOD])
    assert ask_structured(client, MSGS, Ticket).priority == 4
    second = client.calls[1]["messages"]
    assert second[-2] == {"role": "assistant", "content": BAD}
    assert second[-1]["content"].startswith("Your reply was invalid:")
    assert "priority" in second[-1]["content"]
    assert second[-1]["content"].endswith("Fix it and reply with JSON only.")
    assert len(client.calls[0]["messages"]) == 1


def test_gives_up():
    client = FakeClient([BAD])
    with pytest.raises(ValueError, match="could not get a valid reply"):
        ask_structured(client, MSGS, Ticket, max_tries=2)
    assert len(client.calls) == 2


def test_input_list_not_changed():
    msgs = [{"role": "user", "content": "hi"}]
    ask_structured(FakeClient([BAD, GOOD]), msgs, Ticket)
    assert msgs == [{"role": "user", "content": "hi"}], "do not change the list you were given"
