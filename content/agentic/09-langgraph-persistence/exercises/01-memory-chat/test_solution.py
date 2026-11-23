from langchain_core.language_models.fake_chat_models import FakeListChatModel

from solution import build_memory_chat, chat


class Spy(FakeListChatModel):
    seen: list = []

    def _generate(self, messages, *args, **kwargs):
        Spy.seen.append([m.content for m in messages])
        return super()._generate(messages, *args, **kwargs)


def test_chat_returns_the_reply_text():
    app = build_memory_chat(FakeListChatModel(responses=["Hello Dev"]))
    assert chat(app, "t1", "hi") == "Hello Dev"


def test_same_thread_remembers():
    Spy.seen = []
    app = build_memory_chat(Spy(responses=["Hello Dev", "You are Dev"]))
    chat(app, "t1", "I am Dev")
    chat(app, "t1", "Who am I?")
    assert Spy.seen[1] == ["I am Dev", "Hello Dev", "Who am I?"], "the second call must see the whole thread"


def test_other_thread_starts_fresh():
    Spy.seen = []
    app = build_memory_chat(Spy(responses=["a", "b", "c"]))
    chat(app, "t1", "one")
    chat(app, "t2", "two")
    assert Spy.seen[1] == ["two"], "a new thread_id means a new conversation"


def test_app_has_a_checkpointer():
    app = build_memory_chat(FakeListChatModel(responses=["x"]))
    assert app.checkpointer is not None
