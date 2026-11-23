from langchain_core.language_models.fake_chat_models import FakeListChatModel

from solution import build_memory_chat, chat, forget_thread, thread_count, thread_messages


def make():
    return build_memory_chat(FakeListChatModel(responses=["Hello Dev", "Fine"]))


def test_empty_thread():
    app = make()
    assert thread_messages(app, "new") == []
    assert thread_count(app, "new") == 0


def test_thread_messages_in_order():
    app = make()
    chat(app, "t1", "I am Dev")
    chat(app, "t1", "How are you?")
    assert thread_messages(app, "t1") == ["human: I am Dev", "ai: Hello Dev", "human: How are you?", "ai: Fine"]
    assert thread_count(app, "t1") == 4


def test_threads_are_separate():
    app = make()
    chat(app, "a", "one")
    chat(app, "b", "two")
    assert thread_messages(app, "a")[0] == "human: one"
    assert thread_messages(app, "b")[0] == "human: two"


def test_forget_thread_clears_it():
    app = make()
    chat(app, "t1", "secret")
    chat(app, "t2", "keep")
    forget_thread(app, "t1")
    assert thread_messages(app, "t1") == []
    assert thread_count(app, "t2") == 2, "other threads stay"
