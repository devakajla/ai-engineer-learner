from types import SimpleNamespace as NS


class FakeClient:
    def __init__(self, texts):
        self.texts = list(texts)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.texts.pop(0)))])

from solution import cache_key, cached_call

MSG = [{"role": "user", "content": "hi"}]


def test_second_call_is_cached():
    client, cache = FakeClient(["Hello!", "other"]), {}
    assert cached_call(cache, client, MSG) == {"text": "Hello!", "cached": False}
    assert cached_call(cache, client, MSG) == {"text": "Hello!", "cached": True}
    assert len(client.calls) == 1


def test_cache_is_filled_in_place():
    client, cache = FakeClient(["Hello!"]), {}
    cached_call(cache, client, MSG)
    assert cache == {cache_key("qwen/qwen3.8-27b", MSG, 0): "Hello!"}


def test_hot_temperature_is_not_cached():
    client, cache = FakeClient(["a", "b"]), {}
    first = cached_call(cache, client, MSG, temperature=0.7)
    second = cached_call(cache, client, MSG, temperature=0.7)
    assert (first["text"], second["text"]) == ("a", "b")
    assert cache == {} and len(client.calls) == 2


def test_different_messages_are_different_entries():
    client, cache = FakeClient(["a", "b"]), {}
    cached_call(cache, client, MSG)
    out = cached_call(cache, client, [{"role": "user", "content": "other"}])
    assert out == {"text": "b", "cached": False} and len(cache) == 2


def test_call_arguments():
    client = FakeClient(["a"])
    cached_call({}, client, MSG, model="m2")
    assert client.calls[0] == {"model": "m2", "messages": MSG, "temperature": 0}
