"""Step 7 checks. Runs with the current directory = the learner's project folder."""

from types import SimpleNamespace as NS

from copilot.llm import SYSTEM_PROMPT, chat_turn
from copilot.memory import estimate_tokens, trim_last, trim_to_budget
from copilot.spec_tools import ask_spec
from copilot.summary import summarize_old


def reply(content=None, tool_calls=None):
    return NS(choices=[NS(message=NS(role="assistant", content=content, tool_calls=tool_calls), finish_reason="stop")])


class FakeClient:
    def __init__(self, text="ok"):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return reply(self.text)


def msg(role, size):
    return {"role": role, "content": "x" * size}


H = [msg("user", 12), msg("assistant", 16), msg("user", 8), msg("assistant", 8)]   # 3, 4, 2, 2 tokens


def test_earlier_steps_still_work():
    client = FakeClient("Hi!")
    assert chat_turn(client, [], "Hello")[0] == "Hi!"
    assert ask_spec(FakeClient("plain"), {"paths": {}}, "Hello") == "plain"


def test_estimate_tokens():
    assert estimate_tokens("") == 0 and estimate_tokens("abcd") == 1 and estimate_tokens("abcde") == 2


def test_trim_last():
    assert trim_last(["a", "b", "c", "d"], 2) == ["c", "d"]
    assert trim_last(["a", "b"], 9) == ["a", "b"]
    assert trim_last(["a", "b"], 0) == [], "n = 0 must give []"


def test_trim_to_budget():
    assert trim_to_budget(H, 5) == H[2:]
    assert trim_to_budget(H, 100) == H
    assert trim_to_budget(H, 1) == []
    small = [msg("user", 4), msg("assistant", 40), msg("user", 4)]
    assert trim_to_budget(small, 5) == [small[2]], "stop at the first message that does not fit"


def test_summarize_old():
    history = [{"role": "user", "content": "I am Dev"}, {"role": "assistant", "content": "Hi Dev!"}, msg("user", 4)]
    client = FakeClient("Dev said hello.")
    result = summarize_old(client, history, 1, base_delay=0)
    assert result == [{"role": "user", "content": "Summary of the earlier chat: Dev said hello."}, history[2]]
    assert "user: I am Dev\nassistant: Hi Dev!" in client.calls[0]["messages"][0]["content"]
    assert summarize_old(client, history, 0, base_delay=0)[1:] == [], "keep_last=0 summarizes everything"


def test_summarize_old_short_history_makes_no_call():
    client = FakeClient()
    assert summarize_old(client, H, 4, base_delay=0) == H
    assert client.calls == []


def test_chat_turn_sends_only_the_budget_but_keeps_everything():
    client = FakeClient("answer")
    text, history = chat_turn(client, H, "q" * 8, max_history_tokens=4)
    sent = client.calls[0]["messages"]
    assert sent[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert sent[1:-1] == H[2:], "only the two newest old messages fit in 4 tokens"
    assert sent[-1] == {"role": "user", "content": "q" * 8}
    assert text == "answer"
    assert history[:4] == H and len(history) == 6, "the returned history must stay complete"


def test_chat_turn_without_budget_sends_everything():
    client = FakeClient()
    chat_turn(client, H, "hi")
    assert len(client.calls[0]["messages"]) == 1 + 4 + 1
