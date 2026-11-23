from langchain_core.language_models.fake_chat_models import FakeListChatModel

from solution import build_title_chain, clean_title


def test_clean_title_removes_quotes_and_spaces():
    assert clean_title('  "Rain in Pune"  ') == "Rain in Pune"
    assert clean_title("'Hello'") == "Hello"


def test_clean_title_keeps_first_line_only():
    assert clean_title('"A title"\nHere is why I chose it.') == "A title"


def test_clean_title_plain_text_is_unchanged():
    assert clean_title("Plain") == "Plain"


def test_chain_cleans_the_model_reply():
    chain = build_title_chain(FakeListChatModel(responses=['  "Monsoon Is Here"\nBecause it rains.']))
    assert chain.invoke({"text": "It rained all week in the city."}) == "Monsoon Is Here"


def test_chain_prompt_uses_text_variable():
    chain = build_title_chain(FakeListChatModel(responses=["x"]))
    messages = chain.first.invoke({"text": "About cats"}).to_messages()
    assert messages[0].type == "system" and "title" in messages[0].content.lower()
    assert messages[1].content == "About cats"


def test_last_step_is_a_runnable_lambda():
    chain = build_title_chain(FakeListChatModel(responses=["x"]))
    assert len(chain.steps) == 4, "prompt | model | parser | cleaning step"
