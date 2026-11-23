"""The RAG pipeline: retrieve chunks, put them in the prompt, ask the model, return answer and hits."""

from copilot.embed import embed_texts
from copilot.hybrid import hybrid_search
from copilot.llm import DEFAULT_MODEL, complete_with_retry

RAG_SYSTEM = (
    "Answer the question using only the context. "
    "If the answer is not in the context, reply exactly: I don't know."
)

NO_ANSWER = "I don't know."


def retrieve(collection, question, k=3, embed=embed_texts):
    """The k best chunks for the question, using hybrid search."""
    return hybrid_search(collection, question, k=k, embed=embed)


def format_context(hits):
    """Number the hits from 1 and show where each one came from."""
    blocks = []
    for i, hit in enumerate(hits, start=1):
        label = hit["source"]
        if hit.get("heading"):
            label = label + " > " + hit["heading"]
        blocks.append(f"[{i}] {label}\n{hit['text']}")
    return "\n\n".join(blocks)


def build_rag_messages(question, hits):
    """System rules first, then one user message with the context and the question."""
    context = format_context(hits) or "(no context)"
    user = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": user},
    ]


def answer(client, collection, question, k=3, embed=embed_texts, model=DEFAULT_MODEL, base_delay=1.0):
    """Answer from the docs. With no chunks found, say so WITHOUT calling the model.

    Returns {"answer": text, "hits": [...]}.
    """
    hits = retrieve(collection, question, k=k, embed=embed)
    if not hits:
        return {"answer": NO_ANSWER, "hits": []}
    messages = build_rag_messages(question, hits)
    text = complete_with_retry(
        client, messages, model=model, base_delay=base_delay, temperature=0, max_completion_tokens=300
    )
    return {"answer": text, "hits": hits}
