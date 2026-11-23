"""Better retrieval: rerank, rewrite the question, ask in several ways and fuse the results."""

from copilot.bm25 import tokenize
from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.hybrid import reciprocal_rank_fusion
from copilot.llm import DEFAULT_MODEL, complete_with_retry
from copilot.rag import retrieve


def overlap_score(question, text):
    """A tiny stand-in for a reranker: how many different question words appear in the text.

    A real reranker is a cross-encoder model. It has the same shape: (question, text) -> number.
    """
    words = set(tokenize(question))
    return len(words & set(tokenize(text)))


def by_rerank(hit):
    return hit["rerank_score"]


def rerank(score_fn, question, hits, top_n):
    """Score each hit with score_fn(question, text), best first, keep top_n. The input hits are not changed."""
    if top_n <= 0:
        return []
    scored = []
    for hit in hits:
        new_hit = dict(hit)
        new_hit["rerank_score"] = score_fn(question, hit["text"])
        scored.append(new_hit)
    scored = sorted(scored, key=by_rerank, reverse=True)
    return scored[:top_n]


def retrieve_reranked(collection, question, k=3, pool=10, score_fn=overlap_score, embed=embed_texts):
    """Get a wide pool of candidates, then keep the k best after reranking."""
    candidates = retrieve(collection, question, k=pool, embed=embed)
    return rerank(score_fn, question, candidates, k)


def rewrite_question(client, history, question, model=DEFAULT_MODEL, base_delay=1.0):
    """Turn a follow-up like "and for deleting?" into a question that stands alone.

    With no history there is nothing to fix: return the question and do NOT call the model.
    """
    if not history:
        return question
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    prompt = (
        "Rewrite the last question so it can be understood without the chat. "
        "Reply with the question only.\n\n"
        f"Chat:\n{transcript}\n\nLast question: {question}"
    )
    text = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, base_delay=base_delay,
        temperature=0, max_completion_tokens=100,
    )
    return text.strip()


def multi_query(client, question, n=3, model=DEFAULT_MODEL, base_delay=1.0):
    """The question plus up to n different ways to ask it. No repeats (ignoring case)."""
    prompt = f"Write {n} different ways to ask this question, one per line, no numbering:\n{question}"
    text = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, base_delay=base_delay,
        temperature=0.7, max_completion_tokens=200,
    )
    seen = [question.lower()]
    queries = [question]
    for line in text.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if line and line.lower() not in seen:
            seen.append(line.lower())
            queries.append(line)
    return queries[: n + 1]


def retrieve_multi(collection, queries, k=3, embed=embed_texts):
    """Retrieve for every query, fuse the rankings with RRF, return the best k hits."""
    rankings = []
    by_id = {}
    for query in queries:
        hits = retrieve(collection, query, k=k, embed=embed)
        rankings.append([hit["id"] for hit in hits])
        for hit in hits:
            if hit["id"] not in by_id:
                by_id[hit["id"]] = hit
    fused = reciprocal_rank_fusion(rankings)
    return [by_id[item] for item, _ in fused[:k]]


def answer_with_history(client, collection, history, question, k=3, embed=embed_texts, model=DEFAULT_MODEL, base_delay=1.0):
    """A chat turn for RAG: make the question stand alone, then answer it with citations.

    Returns the cited_answer dict plus "query": the question that was really searched.
    """
    query = rewrite_question(client, history, question, model=model, base_delay=base_delay)
    result = cited_answer(client, collection, query, k=k, embed=embed, model=model, base_delay=base_delay)
    result["query"] = query
    return result
