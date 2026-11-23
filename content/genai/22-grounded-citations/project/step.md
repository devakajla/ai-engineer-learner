# Step 13 — Grounded answers with citations

A RAG answer without sources is hard to trust. In this step Copilot cites the chunk numbers it used, like `[1]`, and your **code checks** the citations (lesson 22). A model may cite `[7]` when there are only 3 chunks, or forget to cite at all. Never trust. Check.

### 1. The citation module: `copilot/citations.py`

```python
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
```

Read `cited_answer` slowly:

1. **No hits, no model call.** Same rule as step 12.
2. **Ask with the citation rule.** `CITE_SYSTEM` adds one sentence to the RAG rules.
3. **"I don't know" is a good answer.** It needs no citation, so it is accepted at once. Without this line, an honest refusal would look like a failure.
4. **Check in code.** `check_citations` needs at least one valid number and no invalid number.
5. **Repair once.** Put the bad answer in the messages as an `assistant` message, then tell the model exactly what is wrong. This is the same repair loop as step 5.
6. **Give up clearly.** After `max_tries`, return `ok: False` and **no sources**. The caller must not show invented sources.

`extract_citations` walks the text with a `while` loop. `[docs]` and `[1a]` are not citations because `inner.isdigit()` is false. `sources_from_answer` returns only the hits that were really cited. That is what you show the user.

A check like this proves the numbers point at real chunks. It does **not** prove the answer is true. That needs an LLM judge (step 19).

### 2. Use it in the command: `copilot/rag_cli.py`

Change two things: import `cited_answer` instead of `answer`, and print the cited sources and a warning:

```python
from copilot.citations import cited_answer
...
    result = cited_answer(get_client(), collection, " ".join(sys.argv[1:]))
    print(result["answer"])
    print()
    if not result["ok"]:
        print("Warning: the citations could not be checked. Do not trust this answer.")
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")
```

```bash
uv run python -m copilot.rag_cli "how do I delete a task"
```

You should see an answer with `[1]` style markers, and below it only the sources it cited.

### 3. Commit

```bash
git add -A && git commit -m "Add grounded answers with checked citations"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 12)
│   └── citations.py
├── docs/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `extract_citations` (order, repeats, `[text]`, `[]`, `[1a]`, a missing `]`), `check_citations` (valid, invalid, none, `[0]`), `sources_from_answer`, `build_cite_messages`, and `cited_answer` with a fake client: the happy path, one repair (the repair message must contain the bad answer and the range), giving up with `ok: False` and no sources, accepting "I don't know", and no model call when there are no hits. Steps 1 to 12 must keep working.
