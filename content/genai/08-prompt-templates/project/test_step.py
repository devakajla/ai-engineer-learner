"""Step 4 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

import pytest

from copilot import prompts
from copilot.llm import SYSTEM_PROMPT, chat_turn
from copilot.prompts import PROMPTS, get_prompt, render
from copilot.qa import answer_from_text


class FakeClient:
    def __init__(self, text="It returns all tasks."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({"model": kwargs["model"], "messages": list(kwargs["messages"])})
        return NS(choices=[NS(message=NS(role="assistant", content=self.text), finish_reason="stop")])


def test_earlier_steps_still_work():
    client = FakeClient("Hi!")
    reply, history = chat_turn(client, [], "Hello")
    assert reply == "Hi!" and len(history) == 2


def test_two_versions_of_qa_exist():
    assert "v1" in PROMPTS["qa"] and "v2" in PROMPTS["qa"], "keep v1 and add v2 under PROMPTS['qa']"
    for version, text in PROMPTS["qa"].items():
        assert "{document}" in text and "{question}" in text, f"qa {version} needs {{document}} and {{question}}"


def test_latest_prompt_has_the_safety_patterns():
    text = get_prompt("qa")
    assert "<document>" in text and "</document>" in text, "the latest prompt must wrap the document in <document> tags"
    assert "I don't know" in text, "the latest prompt must tell the model what to reply when the answer is missing"
    assert text == PROMPTS["qa"]["v2"]


def test_get_prompt_with_version():
    assert get_prompt("qa", "v1") == PROMPTS["qa"]["v1"]


def test_latest_version_compares_numbers(monkeypatch):
    monkeypatch.setitem(prompts.PROMPTS, "demo", {"v2": "two", "v10": "ten", "v1": "one"})
    assert get_prompt("demo") == "ten", "v10 is later than v2: compare the numbers, not the text"


def test_render():
    assert render("Hi {name}!", {"name": "Dev"}) == "Hi Dev!"
    with pytest.raises(ValueError) as info:
        render("Hi {name}!", {})
    assert "missing variable: name" in str(info.value)


def test_answer_from_text_sends_document_and_question():
    client = FakeClient("It returns all tasks.")
    reply = answer_from_text(client, " What does GET /tasks do? ", "\nGET /tasks returns all tasks.\n", base_delay=0)
    assert reply == "It returns all tasks."
    messages = client.calls[0]["messages"]
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}, "the system prompt goes first"
    assert messages[-1]["role"] == "user"
    content = messages[-1]["content"]
    assert "GET /tasks returns all tasks." in content, "the document must be in the prompt"
    assert "Question: What does GET /tasks do?" in content, "the (stripped) question must be in the prompt"
    assert len(messages) == 2


def test_answer_from_text_version():
    client = FakeClient()
    answer_from_text(client, "Q?", "D", version="v1", base_delay=0)
    assert client.calls[0]["messages"][-1]["content"] == "Document:\nD\n\nQuestion: Q?"
