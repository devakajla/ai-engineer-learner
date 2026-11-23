from langchain_core.language_models.fake_chat_models import FakeListChatModel

from solution import build_chain


def test_returns_plain_text():
    chain = build_chain(FakeListChatModel(responses=["Hola"]))
    out = chain.invoke({"language": "Spanish", "text": "Hello"})
    assert out == "Hola", "the chain must return a plain string (add the output parser)"
    assert isinstance(out, str)


def test_prompt_has_system_and_human_message():
    chain = build_chain(FakeListChatModel(responses=["x"]))
    messages = chain.first.invoke({"language": "French", "text": "Good night"}).to_messages()
    assert [m.type for m in messages] == ["system", "human"], "first a system message, then a human message"
    assert messages[0].content == "Translate the text to French. Reply with the translation only."
    assert messages[1].content == "Good night"


def test_chain_is_reusable():
    chain = build_chain(FakeListChatModel(responses=["uno", "dos"]))
    assert chain.invoke({"language": "Spanish", "text": "one"}) == "uno"
    assert chain.invoke({"language": "Spanish", "text": "two"}) == "dos"


def test_missing_variable_fails():
    chain = build_chain(FakeListChatModel(responses=["x"]))
    try:
        chain.invoke({"text": "hi"})
    except KeyError:
        return
    raise AssertionError("the prompt needs both language and text")
