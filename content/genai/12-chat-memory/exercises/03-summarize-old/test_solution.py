from types import SimpleNamespace as NS

from solution import summarize_old


class FakeClient:
    def __init__(self, text="Dev introduced himself."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(role="assistant", content=self.text))])


H = [
    {"role": "user", "content": "I am Dev"},
    {"role": "assistant", "content": "Hi Dev!"},
    {"role": "user", "content": "What is a list?"},
    {"role": "assistant", "content": "An ordered collection."},
    {"role": "user", "content": "And a tuple?"},
]
SUMMARY = {"role": "user", "content": "Summary of the earlier chat: Dev introduced himself."}


def test_summarizes_the_old_part():
    client = FakeClient()
    assert summarize_old(client, H, 2) == [SUMMARY] + H[3:]
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["model"] == "qwen/qwen3.8-27b" and call["temperature"] == 0
    assert call["messages"] == [
        {
            "role": "user",
            "content": "Summarize this conversation in 2 sentences:\n"
            "user: I am Dev\nassistant: Hi Dev!\nuser: What is a list?",
        }
    ]


def test_keep_zero_summarizes_everything():
    client = FakeClient()
    assert summarize_old(client, H, 0) == [SUMMARY], "keep_last=0 means every message is old"
    assert "user: And a tuple?" in client.calls[0]["messages"][0]["content"]


def test_short_history_needs_no_call():
    client = FakeClient()
    result = summarize_old(client, H, 5)
    assert result == H and result is not H, "return a copy"
    assert summarize_old(client, H, 9) == H
    assert client.calls == [], "do not call the model when nothing is old"


def test_input_is_not_changed():
    before = list(H)
    summarize_old(FakeClient(), H, 2)
    assert H == before
