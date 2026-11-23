from types import SimpleNamespace as NS


class FakeClient:
    """Returns the replies one by one (the last one repeats). Records every call."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.replies) - 1)
        return NS(choices=[NS(message=NS(content=self.replies[index]))])


def user_text(call):
    return call["messages"][-1]["content"]


from solution import compress_history


def chat(n):
    return [{"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(n)]


def test_short_history_is_unchanged_and_costs_nothing():
    client = FakeClient("unused")
    messages = chat(4)
    assert compress_history(client, messages, keep_last=4) == messages
    assert client.calls == [], "no model call when nothing needs compressing"


def test_older_messages_become_one_summary():
    client = FakeClient("They greeted each other.")
    out = compress_history(client, chat(8), keep_last=3)
    assert out[0] == {"role": "system", "content": "Summary of the earlier chat: They greeted each other."}
    assert [m["content"] for m in out[1:]] == ["m5", "m6", "m7"], "the last 3 messages stay word for word"
    assert len(out) == 4


def test_the_summary_prompt_contains_only_the_older_messages():
    client = FakeClient("s")
    compress_history(client, chat(6), keep_last=2)
    prompt = user_text(client.calls[0])
    assert prompt.startswith("Summarise this chat in 2 short sentences. Keep names and decisions.\n\n")
    assert "user: m0\nassistant: m1\nuser: m2\nassistant: m3" in prompt
    assert "m4" not in prompt and "m5" not in prompt


def test_keep_last_zero_summarises_everything():
    client = FakeClient("all of it")
    out = compress_history(client, chat(3), keep_last=0)
    assert out == [{"role": "system", "content": "Summary of the earlier chat: all of it"}]
    assert len(client.calls) == 1
