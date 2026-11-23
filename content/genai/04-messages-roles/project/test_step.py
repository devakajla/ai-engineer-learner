"""Step 2 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

from copilot.llm import DEFAULT_MODEL, SYSTEM_PROMPT, ask, build_messages, chat_turn


class FakeClient:
    def __init__(self, replies=("Hello there!",)):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({"model": kwargs["model"], "messages": list(kwargs["messages"])})
        text = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return NS(choices=[NS(message=NS(role="assistant", content=text), finish_reason="stop")])


def test_step1_ask_still_works():
    client = FakeClient(["Hi!"])
    assert ask(client, "Hello") == "Hi!"
    assert client.calls[0]["messages"] == [{"role": "user", "content": "Hello"}]
    assert client.calls[0]["model"] == DEFAULT_MODEL


def test_system_prompt_is_text():
    assert isinstance(SYSTEM_PROMPT, str) and len(SYSTEM_PROMPT) > 20, "SYSTEM_PROMPT should be a real sentence or two"


def test_build_messages_order():
    history = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
    messages = build_messages(history, "c")
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}, "the system message goes first"
    assert [m["content"] for m in messages[1:]] == ["a", "b", "c"]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]


def test_build_messages_does_not_change_history():
    history = [{"role": "user", "content": "a"}]
    build_messages(history, "b")
    assert len(history) == 1, "build_messages must not change the history it receives"


def test_chat_turn_first_turn():
    client = FakeClient(["A REST API uses HTTP."])
    reply, history = chat_turn(client, [], "What is REST?")
    assert reply == "A REST API uses HTTP."
    assert history == [
        {"role": "user", "content": "What is REST?"},
        {"role": "assistant", "content": "A REST API uses HTTP."},
    ], "the returned history has the user message and the assistant reply, and no system message"
    assert client.calls[0]["messages"][0]["role"] == "system"


def test_chat_turn_sends_old_turns():
    client = FakeClient(["one", "two"])
    _, history = chat_turn(client, [], "first")
    reply, history = chat_turn(client, history, "second")
    sent = [m["content"] for m in client.calls[1]["messages"][1:]]
    assert sent == ["first", "one", "second"], "the second call must send the earlier turns"
    assert reply == "two" and len(history) == 4


def test_chat_turn_does_not_change_input_history():
    client = FakeClient(["x"])
    old = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
    chat_turn(client, old, "c")
    assert len(old) == 2, "chat_turn must not change the history it receives"
