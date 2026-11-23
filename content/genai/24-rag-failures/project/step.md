# Step 17 — Fix the context, name the failures

When a RAG answer is bad, "make the prompt better" is a guess. Lesson 24 gives you a better habit: find **where** it broke. Was the right chunk never found (retrieval), was it found but ignored (generation), or was there no answer and the model made one up (hallucination)? Each cause has a different fix. This step gives Copilot two tools: cleaner context, and a failure labeller.

### 1. Cleaner context: `copilot/context.py`

```python
"""Prepare the chunks before they go into the prompt: no repeats, no one-source flood, best at the edges."""

from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import retrieve


def dedupe_hits(hits, max_per_source=None):
    """Drop hits whose text repeats an earlier one (ignoring case and spacing).

    With max_per_source, keep at most that many hits from one source. Order is kept.
    """
    seen = []
    per_source = {}
    kept = []
    for hit in hits:
        normal = " ".join(hit["text"].lower().split())
        if normal in seen:
            continue
        source = hit.get("source", "")
        if max_per_source is not None and per_source.get(source, 0) >= max_per_source:
            continue
        seen.append(normal)
        per_source[source] = per_source.get(source, 0) + 1
        kept.append(hit)
    return kept


def prepare_context(hits, max_hits, max_per_source=2):
    """Dedupe, cut to max_hits, then put the best chunks at the START and END of the list.

    Models use the beginning and the end of a long context best, and lose the middle ("lost in the middle").
    Input is best first. The result is ranks 1, 3, 5 ... then ... 6, 4, 2.
    """
    if max_hits <= 0:
        return []
    hits = dedupe_hits(hits, max_per_source)[:max_hits]
    front = hits[0::2]
    back = hits[1::2]
    back.reverse()
    return front + back


def retrieve_prepared(collection, question, k=3, pool=10, max_per_source=2, embed=embed_texts):
    """A wide pool, cleaned and ordered, ready for the prompt."""
    candidates = retrieve(collection, question, k=pool, embed=embed)
    return prepare_context(candidates, k, max_per_source)


def answer_prepared(client, collection, question, k=3, pool=10, max_per_source=2,
                    embed=embed_texts, model=DEFAULT_MODEL, base_delay=1.0):
    """A cited answer from prepared chunks."""
    hits = retrieve_prepared(collection, question, k=k, pool=pool, max_per_source=max_per_source, embed=embed)
    return cited_answer(client, collection, question, k=k, embed=embed, model=model,
                        base_delay=base_delay, hits=hits)
```

Read it in parts:

1. **`dedupe_hits`** removes chunks with the same text (docs often repeat a paragraph) after lowercasing and squeezing the spaces. The optional `max_per_source` stops one long file from filling the whole prompt. A dropped repeat does not count against the limit: the test checks it.
2. **`prepare_context` reorders on purpose.** Models read the start and the end of a long prompt best, and lose the middle ("lost in the middle"). The input is best-first: ranks 1, 2, 3, 4, 5. The output is 1, 3, 5, 4, 2. `hits[0::2]` takes every second item from the start. `hits[1::2]` takes the others, and `reverse()` puts them at the end. The best two sit at the two edges.
3. **Order of work matters:** dedupe first, cut to `max_hits` after. Otherwise a repeat could use up a slot.
4. **`retrieve_prepared`** is "wide then clean": ask for a pool of 10, keep 3.
5. **`answer_prepared`** hands the prepared list to `cited_answer(hits=...)` (the argument you added in step 16).

Citation numbers follow the **prepared** order, because `format_context` numbers the list it is given. That is fine: the sources are built from the same list.

### 2. Name the failure: `copilot/failures.py`

```python
"""Find out WHY a RAG answer failed. The fix depends on the cause."""

CATEGORIES = ["ok", "retrieval_miss", "generation_miss", "hallucination"]


def classify_failure(expected_ids, retrieved_ids, answer_ok):
    """One label for one question.

    expected_ids: the chunk ids that hold the answer (empty if the docs have no answer).
    retrieved_ids: the chunk ids the search returned.
    answer_ok: did the final answer pass your check?
    """
    if not expected_ids:
        return "ok" if answer_ok else "hallucination"
    found = any(item in retrieved_ids for item in expected_ids)
    if not found:
        return "retrieval_miss"
    if not answer_ok:
        return "generation_miss"
    return "ok"


def failure_report(results):
    """Count the labels and list the questions behind each one.

    Each result is {"question", "expected", "retrieved", "answer_ok"}.
    """
    counts = {name: 0 for name in CATEGORIES}
    by_category = {name: [] for name in CATEGORIES}
    for result in results:
        name = classify_failure(result["expected"], result["retrieved"], result["answer_ok"])
        counts[name] += 1
        by_category[name].append(result["question"])
    return {"counts": counts, "by_category": by_category}
```

The decision is a short chain, in this order:

1. No expected chunk (the docs have no answer)? The answer should be "I don't know". If it is not ok, that is a **hallucination**.
2. Expected chunk not among the retrieved ones? **Retrieval miss.** Fix: chunking, hybrid search, reranking, query rewrite. Changing the prompt will not help, because the model never saw the text.
3. Chunk found but the answer is bad? **Generation miss.** Fix: the prompt, the model, fewer or cleaner chunks, the order of chunks.
4. Otherwise it is fine.

`failure_report` runs this over many questions and lists the questions behind each label. Read the biggest group first: that is where your next hour pays most. In step 18 the evaluation will feed this report.

### 3. Try it

You do not need a model for this part. In a Python shell:

```python
from copilot.failures import failure_report
results = [
    {"question": "q1", "expected": ["a"], "retrieved": ["b"], "answer_ok": False},
    {"question": "q2", "expected": ["a"], "retrieved": ["a"], "answer_ok": False},
]
print(failure_report(results)["counts"])
```

Then add `answer_prepared` to your own flow and compare it with `cited_answer` on a question where one file has many similar chunks.

### 4. Commit

```bash
git add -A && git commit -m "Add context preparation and failure analysis"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 16)
│   ├── context.py
│   └── failures.py
├── docs/
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `dedupe_hits` (case and spacing, the per-source limit, order, dropped repeats not counted), `prepare_context` (the 1, 3, 5, 4, 2 order, dedupe before the cut, the per-source limit, `max_hits=0`), `classify_failure` (all four labels and "any expected chunk is enough"), `failure_report` (counts, questions per label, empty input) and `retrieve_prepared` and `answer_prepared` with a fake embedder and a fake client. Steps 1 to 16 must keep working.
