from types import SimpleNamespace as NS

import pytest

from solution import describe_image


class FakeClient:
    def __init__(self):
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content="A cat on a sofa."))])


def test_call():
    client = FakeClient()
    out = describe_image(client, "vis-model", "What is it?", "https://x/cat.jpg")
    assert out == "A cat on a sofa."
    call = client.calls[0]
    assert call["model"] == "vis-model"
    assert call["max_completion_tokens"] == 300
    content = call["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "What is it?"}
    assert content[1]["image_url"]["url"] == "https://x/cat.jpg"


def test_no_image_no_call():
    client = FakeClient()
    with pytest.raises(ValueError, match="no image"):
        describe_image(client, "m", "q", "")
    assert client.calls == []
