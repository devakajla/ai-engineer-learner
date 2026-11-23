from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from solution import build_rag_chain, format_docs, make_retriever

DOCS = [
    Document(page_content="Tea grows in Assam and Darjeeling", metadata={"source": "tea.md"}),
    Document(page_content="Coffee grows in Karnataka", metadata={"source": "coffee.md"}),
    Document(page_content="Tea needs rain and warm air", metadata={"source": "tea2.md"}),
]


def test_retriever_is_a_runnable_that_returns_documents():
    out = make_retriever(DOCS).invoke("where does tea grow")
    assert all(isinstance(d, Document) for d in out)
    assert out[0].page_content.startswith("Tea grows"), "most shared words first"


def test_retriever_respects_k_and_ignores_zero_scores():
    assert len(make_retriever(DOCS, k=1).invoke("tea")) == 1
    assert make_retriever(DOCS).invoke("zebra") == []


def test_retriever_ties_keep_original_order():
    out = make_retriever(DOCS, k=3).invoke("tea")
    assert [d.metadata["source"] for d in out] == ["tea.md", "tea2.md"]


def test_format_docs_numbers_the_passages():
    assert format_docs(DOCS[:2]) == "[1] Tea grows in Assam and Darjeeling\n[2] Coffee grows in Karnataka"
    assert format_docs([]) == ""


def test_rag_chain_puts_context_and_question_into_the_prompt():
    seen = []

    def fake_model(prompt_value):
        seen.append(prompt_value.to_messages())
        return AIMessage(content="Assam.")

    chain = build_rag_chain(make_retriever(DOCS, k=1), RunnableLambda(fake_model))
    assert chain.invoke("where does tea grow") == "Assam."
    system, human = seen[0]
    assert system.type == "system" and "only the context" in system.content
    assert human.content == (
        "Context:\n[1] Tea grows in Assam and Darjeeling\n\nQuestion: where does tea grow"
    )
