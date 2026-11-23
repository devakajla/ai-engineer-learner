from types import SimpleNamespace as NS

from solution import classify

LABELS = ["positive", "negative"]


class FakeClient:
    def __init__(self, text):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(role="assistant", content=self.text))])


def test_cleans_the_reply():
    assert classify(FakeClient("  Positive.\n"), "I love it", LABELS) == "positive"
    assert classify(FakeClient("NEGATIVE"), "awful", LABELS) == "negative"


def test_unknown_reply():
    assert classify(FakeClient("It is hard to say"), "meh", LABELS) == "unknown"
    assert classify(FakeClient(""), "meh", LABELS) == "unknown"


def test_the_call():
    client = FakeClient("positive")
    classify(client, "I love it", LABELS)
    call = client.calls[0]
    assert call["model"] == "qwen/qwen3.8-27b"
    assert call["temperature"] == 0, "use temperature=0 for classification"
    assert call["messages"] == [
        {
            "role": "user",
            "content": "Classify the text as one of: positive, negative. Answer with only the label.\n\nText: I love it",
        }
    ]
