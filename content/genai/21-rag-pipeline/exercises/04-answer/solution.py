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


def answer(client, retrieve, question, k=3, min_score=0.0):
    hits = [h for h in retrieve(question, k) if h["score"] >= min_score]
    if not hits:
        return {"answer": "I don't know.", "hits": []}
    messages = build_rag_messages(question, hits)
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        temperature=0,
        max_completion_tokens=300,
    )
    return {"answer": response.choices[0].message.content, "hits": hits}
