from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.runnables import RunnableLambda

from solution import build_chain, run_batch, safe_chain


def test_run_batch_returns_one_answer_per_text_in_order():
    chain = build_chain(FakeListChatModel(responses=["uno"]))
    out = run_batch(chain, ["one", "two", "three"], "Spanish")
    assert out == ["uno", "uno", "uno"]


def test_run_batch_empty_list():
    chain = build_chain(FakeListChatModel(responses=["x"]))
    assert run_batch(chain, [], "Spanish") == []


def test_run_batch_sends_language_and_text():
    seen = []

    def spy(value):
        seen.append(value)
        return "ok"

    out = run_batch(RunnableLambda(spy), ["a", "b"], "French")
    assert out == ["ok", "ok"]
    assert {"language": "French", "text": "a"} in seen and {"language": "French", "text": "b"} in seen


def broken(_):
    raise RuntimeError("model is down")


def test_safe_chain_uses_main_when_it_works():
    chain = safe_chain(RunnableLambda(lambda x: "main"), RunnableLambda(lambda x: "backup"))
    assert chain.invoke("q") == "main"


def test_safe_chain_falls_back_on_error():
    chain = safe_chain(RunnableLambda(broken), RunnableLambda(lambda x: "backup"))
    assert chain.invoke("q") == "backup"


def test_safe_chain_still_fails_when_both_fail():
    chain = safe_chain(RunnableLambda(broken), RunnableLambda(broken))
    try:
        chain.invoke("q")
    except RuntimeError:
        return
    raise AssertionError("when the backup also fails the error must come out")
