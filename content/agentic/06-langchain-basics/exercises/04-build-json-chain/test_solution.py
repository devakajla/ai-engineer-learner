from langchain_core.language_models.fake_chat_models import FakeListChatModel

from solution import build_json_chain


def test_returns_a_dict():
    chain = build_json_chain(FakeListChatModel(responses=['{"name": "Asha", "age": 21}']))
    out = chain.invoke({"sentence": "Asha is 21 years old."})
    assert out == {"name": "Asha", "age": 21}, "the parser must turn the JSON text into a dict"


def test_fenced_json_is_accepted():
    reply = '```json\n{"name": "Ravi", "age": 30}\n```'
    chain = build_json_chain(FakeListChatModel(responses=[reply]))
    assert chain.invoke({"sentence": "Ravi is 30."}) == {"name": "Ravi", "age": 30}


def test_prompt_shows_the_shape_and_keeps_the_sentence():
    chain = build_json_chain(FakeListChatModel(responses=["{}"]))
    messages = chain.first.invoke({"sentence": "Meera is 40."}).to_messages()
    assert '{"name": "<person name>", "age": <number>}' in messages[0].content, "show the JSON shape in the system message"
    assert messages[1].content == "Meera is 40."


def test_bad_json_raises():
    chain = build_json_chain(FakeListChatModel(responses=["not json at all"]))
    try:
        chain.invoke({"sentence": "x"})
    except Exception:
        return
    raise AssertionError("text that is not JSON must raise an error")
