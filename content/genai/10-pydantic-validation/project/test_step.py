"""Step 5 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

import pytest
from pydantic import ValidationError

from copilot.llm import chat_turn, complete_with_retry
from copilot.prompts import get_prompt
from copilot.qa import answer_from_text, answer_structured
from copilot.schemas import Answer

GOOD = '{"answer": "Call GET /tasks.", "found": true, "confidence": "high", "quote": "GET /tasks returns all tasks."}'
BAD = '{"answer": "Call GET /tasks.", "found": true, "confidence": "certain"}'


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        text = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return NS(choices=[NS(message=NS(role="assistant", content=text), finish_reason="stop")])


def test_earlier_steps_still_work():
    client = FakeClient(["Hi!"])
    reply, history = chat_turn(client, [], "Hello")
    assert reply == "Hi!" and len(history) == 2
    assert answer_from_text(FakeClient(["text"]), "Q?", "D", base_delay=0) == "text"
    assert "response_format" not in client.calls[0], "do not send response_format unless it is asked for"


def test_answer_model():
    a = Answer(answer="x", found=True, confidence="high")
    assert a.quote == "", "quote is optional and defaults to an empty string"
    for bad in ("certain", "HIGH", ""):
        with pytest.raises(ValidationError):
            Answer(answer="x", found=True, confidence=bad)
    with pytest.raises(ValidationError):
        Answer(answer="x", confidence="low")


def test_complete_with_retry_passes_response_format():
    client = FakeClient(["{}"])
    complete_with_retry(client, [{"role": "user", "content": "hi"}], base_delay=0, response_format={"type": "json_object"})
    assert client.calls[0]["response_format"] == {"type": "json_object"}


def test_qa_json_prompt():
    text = get_prompt("qa_json")
    assert "{document}" in text and "{question}" in text
    assert "JSON" in text, "the prompt must say JSON (JSON mode needs it)"
    assert "{{" in text, "write the example shape with doubled braces {{ }}"


def test_answer_structured_good_reply():
    client = FakeClient([GOOD])
    result = answer_structured(client, "How do I list tasks?", "GET /tasks returns all tasks.", base_delay=0)
    assert isinstance(result, Answer)
    assert result.found is True and result.confidence == "high"
    assert result.quote == "GET /tasks returns all tasks."
    call = client.calls[0]
    assert call["response_format"] == {"type": "json_object"}, "turn on JSON mode"
    content = call["messages"][-1]["content"]
    assert "GET /tasks returns all tasks." in content and "How do I list tasks?" in content


def test_answer_structured_repairs():
    client = FakeClient([BAD, GOOD])
    result = answer_structured(client, "Q?", "D", base_delay=0)
    assert result.confidence == "high"
    assert len(client.calls) == 2
    second = client.calls[1]["messages"]
    assert second[-2] == {"role": "assistant", "content": BAD}, "send the bad reply back"
    assert "Your reply was invalid:" in second[-1]["content"] and "confidence" in second[-1]["content"]


def test_answer_structured_gives_up():
    client = FakeClient([BAD])
    with pytest.raises(ValueError, match="could not get a valid answer"):
        answer_structured(client, "Q?", "D", max_tries=2, base_delay=0)
    assert len(client.calls) == 2
