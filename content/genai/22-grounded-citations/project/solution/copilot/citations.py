"""Citations: ask the model to cite context numbers like [1], then CHECK them in code."""

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL, complete_with_retry
from copilot.rag import NO_ANSWER, RAG_SYSTEM, build_rag_messages, retrieve

CITE_SYSTEM = RAG_SYSTEM + " After each fact, cite the context number in square brackets, like [1]."


def extract_citations(answer):
    """The numbers in [n] markers, in order, without repeats. [text] and [] are ignored."""
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
    """Split the cited numbers into valid (1..n_hits) and invalid. ok needs a valid one and no invalid one."""
    cited = extract_citations(answer)
    valid = [n for n in cited if 1 <= n <= n_hits]
    invalid = [n for n in cited if n < 1 or n > n_hits]
    return {"cited": valid, "invalid": invalid, "ok": bool(valid) and not invalid}


def sources_from_answer(answer, hits):
    """The hits the answer really cited, as {"n", "source", "heading"}."""
    sources = []
    for n in extract_citations(answer):
        if 1 <= n <= len(hits):
            hit = hits[n - 1]
            sources.append({"n": n, "source": hit["source"], "heading": hit.get("heading", "")})
    return sources


def build_cite_messages(question, hits):
    """The RAG messages, with the system rule that asks for citations."""
    messages = build_rag_messages(question, hits)
    return [{"role": "system", "content": CITE_SYSTEM}, messages[1]]


def cited_answer(client, collection, question, k=3, embed=embed_texts, model=DEFAULT_MODEL,
                 base_delay=1.0, max_tries=2):
    """Answer with checked citations. One repair try if the citations are missing or wrong.

    Returns {"answer", "sources", "ok", "hits"}. ok is False when the citations could not be fixed.
    """
    hits = retrieve(collection, question, k=k, embed=embed)
    if not hits:
        return {"answer": NO_ANSWER, "sources": [], "ok": True, "hits": []}
    messages = build_cite_messages(question, hits)
    text = ""
    for _ in range(max_tries):
        text = complete_with_retry(
            client, messages, model=model, base_delay=base_delay, temperature=0, max_completion_tokens=300
        )
        if text.strip().lower().startswith("i don't know"):
            return {"answer": text, "sources": [], "ok": True, "hits": hits}
        if check_citations(text, len(hits))["ok"]:
            return {"answer": text, "sources": sources_from_answer(text, hits), "ok": True, "hits": hits}
        messages = messages + [
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": f"Your answer must cite sources like [1]. Use only the numbers 1 to {len(hits)}. Rewrite it.",
            },
        ]
    return {"answer": text, "sources": [], "ok": False, "hits": hits}
