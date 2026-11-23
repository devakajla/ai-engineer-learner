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


def extract_citations(answer):
    numbers = []
    i = 0
    while i < len(answer):
        if answer[i] == "[":
            j = answer.find("]", i)
            if j == -1:
                break
            inner = answer[i + 1:j]
            if inner.isdigit():
                n = int(inner)
                if n not in numbers:
                    numbers.append(n)
                i = j + 1
                continue
        i += 1
    return numbers


def check_citations(answer, n_hits):
    cited = extract_citations(answer)
    valid = [n for n in cited if 1 <= n <= n_hits]
    invalid = [n for n in cited if n < 1 or n > n_hits]
    return {"cited": valid, "invalid": invalid, "ok": bool(valid) and not invalid}


def sources_from_answer(answer, hits):
    sources = []
    for n in extract_citations(answer):
        if 1 <= n <= len(hits):
            hit = hits[n - 1]
            sources.append({"n": n, "source": hit["source"], "heading": hit.get("heading", "")})
    return sources


CITE_SYSTEM = (
    RAG_SYSTEM
    + " After each fact, cite the context number in square brackets, like [1]."
)


def build_cite_messages(question, hits):
    messages = build_rag_messages(question, hits)
    return [{"role": "system", "content": CITE_SYSTEM}, messages[1]]


def cited_answer(client, retrieve, question, k=3):
    hits = retrieve(question, k)
    if not hits:
        return {"answer": "I don't know.", "sources": [], "ok": True}
    messages = build_cite_messages(question, hits)
    text = ""
    for _ in range(2):
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b", messages=messages, temperature=0, max_completion_tokens=300
        )
        text = response.choices[0].message.content
        if text.strip().lower().startswith("i don't know"):
            return {"answer": text, "sources": [], "ok": True}
        if check_citations(text, len(hits))["ok"]:
            return {"answer": text, "sources": sources_from_answer(text, hits), "ok": True}
        messages = messages + [
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": f"Your answer must cite sources like [1]. Use only the numbers 1 to {len(hits)}. Rewrite it.",
            },
        ]
    return {"answer": text, "sources": [], "ok": False}
