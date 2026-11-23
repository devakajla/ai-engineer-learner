# Step 14 — Rerank, rewrite and multi-query

Copilot answers well when the right chunk is in the top 3. This step raises the odds (lesson 23):

- **Rerank**: fetch a wide pool, then re-score it with a more careful scorer and keep the best.
- **Rewrite**: a follow-up like "and for deleting?" means nothing alone. Turn it into a full question first.
- **Multi-query**: ask the same thing in a few ways and fuse the results with RRF.

### 1. `copilot/rewrite.py`

```python
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
```

Read it in parts:

1. **`overlap_score` is a toy reranker.** It counts how many different question words the text contains. A real reranker is a **cross-encoder** model that reads the question and the text together. It has the same shape, `(question, text) -> number`, so you can swap it in later without changing `rerank`. `score_fn` is passed as an argument: no global, no closure.
2. **`rerank` copies each hit** (`dict(hit)`) before adding `rerank_score`. The caller's hits stay untouched. A function that quietly changes its input is a bug waiting to happen.
3. **`retrieve_reranked` is "wide then narrow".** Hybrid search is fast but rough, so ask for 10 candidates. Then spend the extra effort on only those 10 and keep 3.
4. **`rewrite_question` does nothing without history.** No history means the question already stands alone. Return it and spend no model call.
5. **`multi_query` cleans the model's lines.** Models add bullets and repeat the question. Strip the bullet characters, ignore case when removing repeats, and cut to `n + 1` queries. The original question always stays first. A higher temperature (0.7) gives different phrasings. This is one of the few places where variety is the goal.
6. **`retrieve_multi` fuses by chunk id.** Each query gives a ranking. `reciprocal_rank_fusion` (step 11) joins them. A chunk that shows up for several phrasings rises.
7. **`answer_with_history`** is the RAG chat turn: rewrite, then cited answer. It also returns the `query` it really searched, which is the first thing to look at when an answer is bad.

### 2. A chat in the terminal: `copilot/rag_cli.py`

Replace the file with:

```python
"""Talk to your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.rag_cli                      # a chat, follow-up questions work
    python -m copilot.rag_cli "how do I delete a task"   # one question
"""

import sys

from copilot.llm import get_client
from copilot.rewrite import answer_with_history
from copilot.store import open_collection

DB_PATH = ".chroma"


def ask_once(client, collection, history, question):
    """One turn. Returns the new history (the plain question and the answer text)."""
    result = answer_with_history(client, collection, history, question)
    print(result["answer"])
    if not result["ok"]:
        print("Warning: the citations could not be checked. Do not trust this answer.")
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")
    return history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": result["answer"]},
    ]


def main():
    client = get_client()
    collection = open_collection(DB_PATH)
    if len(sys.argv) > 1:
        ask_once(client, collection, [], " ".join(sys.argv[1:]))
        return
    history = []
    print("Ask about your docs. Type 'quit' to stop.")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if question:
            history = ask_once(client, collection, history[-6:], question)


if __name__ == "__main__":
    main()
```

`history[-6:]` keeps only the last 6 messages for the rewrite. A rewrite needs the last turn or two, not the whole chat. (The history here stores the plain questions and answers.)

```bash
uv run python -m copilot.rag_cli
```

Ask "How do I create a task?" and then "and how do I delete one?". Watch the answer: the second one only works because of the rewrite. Print `result["query"]` once if you want to see the rewritten question.

### 3. Commit

```bash
git add -A && git commit -m "Add rerank, question rewrite and multi-query retrieval"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 13)
│   └── rewrite.py
├── docs/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `overlap_score` (different words, repeats), `rerank` (order, cut, input not changed, `top_n=0`), `retrieve_reranked`, `rewrite_question` (no history means no model call, the prompt holds the chat, the answer is stripped), `multi_query` (bullets removed, repeats removed ignoring case, original first, temperature above 0), `retrieve_multi` (no repeated chunks, empty queries) and `answer_with_history` with a fake client: with history it makes two calls and returns the rewritten `query`, without history one call. Steps 1 to 13 must keep working.
