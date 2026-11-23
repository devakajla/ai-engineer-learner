# Given from earlier exercises. Do not change these.
def format_context(hits):
    blocks = []
    for i, hit in enumerate(hits, start=1):
        label = hit["source"]
        if hit.get("heading"):
            label = label + " > " + hit["heading"]
        blocks.append(f"[{i}] {label}\n{hit['text']}")
    return "\n\n".join(blocks)


RAG_SYSTEM = (
    "Answer the question using only the context. "
    "If the answer is not in the context, reply exactly: I don't know."
)


def build_rag_messages(question, hits):
    context = format_context(hits) or "(no context)"
    user = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": user},
    ]
