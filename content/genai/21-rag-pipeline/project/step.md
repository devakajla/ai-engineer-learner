# Step 12 — The RAG pipeline

Until now Copilot could **search** (steps 8 to 11) and **chat** (steps 1 to 7). In this step you join them: find the best chunks, put them in the prompt, and let the model answer from them. This is RAG (lesson 21).

### 1. Two small options for `complete_with_retry`

Open `copilot/llm.py`. Grounded answers need `temperature=0` and a limit on the length. Add two optional arguments to `complete_with_retry`, and pass them on only when they are given:

```python
def complete_with_retry(
    client, messages, model=DEFAULT_MODEL, max_tries=3, base_delay=1.0, response_format=None,
    temperature=None, max_completion_tokens=None,
):
    ...
    options = {}
    if response_format is not None:
        options["response_format"] = response_format
    if temperature is not None:
        options["temperature"] = temperature
    if max_completion_tokens is not None:
        options["max_completion_tokens"] = max_completion_tokens
```

Why "only when given"? Old code that does not pass them must behave exactly as before. A change that keeps the old calls working is the safe kind.

### 2. The pipeline: `copilot/rag.py`

```python
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
```

Read `answer` slowly:

1. **Retrieve.** `hybrid_search` from step 11 gives the best `k` chunks.
2. **Stop early.** No chunks means nothing to ground an answer on. Return "I don't know." and do **not** call the model. That saves money and removes a chance to make things up.
3. **Build the prompt.** The chunks are numbered `[1]`, `[2]`. The numbers are not decoration: step 13 uses them for citations.
4. **Ask with `temperature=0`.** A grounded answer should be the same each time.
5. **Return the hits too.** The caller needs them to show sources and, later, to evaluate.

The `embed` argument is passed down so tests can use a fake embedder. Real use leaves the default.

### 3. A command to try it: `copilot/rag_cli.py`

```python
"""Ask a question about your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.rag_cli "how do I delete a task"
"""

import sys

from copilot.llm import get_client
from copilot.rag import answer
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    result = answer(get_client(), collection, " ".join(sys.argv[1:]))
    print(result["answer"])
    print()
    for i, hit in enumerate(result["hits"], start=1):
        print(f"[{i}] {hit['source']} > {hit['heading']}")


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.docs_cli index docs
uv run python -m copilot.rag_cli "how do I delete a task"
uv run python -m copilot.rag_cli "what is the price of the moon"
```

The second question has no answer in your docs. A good Copilot says "I don't know." Try it, and look at the numbered sources it prints.

### 4. Commit

```bash
git add -A && git commit -m "Add the RAG pipeline"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 11)
│   ├── rag.py
│   └── rag_cli.py
├── docs/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check that `complete_with_retry` only sends `temperature` and `max_completion_tokens` when you give them, `format_context` (numbering, `source > heading`, empty input), `build_rag_messages` (roles, rules, the `(no context)` text), `retrieve`, and `answer` with a fake client: the chunk text must be in the prompt, `temperature` must be 0, and an empty index must **not** call the model. Steps 1 to 11 must keep working.
