# Step 18 — Measure retrieval with a golden set

"It feels better" is not a result. In this step Copilot gets a **golden set** (questions with the chunks that should answer them) and three numbers (lesson 25). You can then change the chunk size, the search or the reranker, run the numbers again, and **know** if it helped.

### 1. `copilot/evals.py`

```python
"""Measure retrieval with numbers. A change you cannot measure is only a feeling."""

import json
from pathlib import Path

from copilot.embed import embed_texts
from copilot.hybrid import keyword_search
from copilot.rag import retrieve
from copilot.store import search


def recall_at_k(expected_ids, retrieved_ids, k):
    """The share of expected chunks found in the first k results. No expected chunks gives 1.0."""
    if not expected_ids:
        return 1.0
    top = retrieved_ids[:k] if k > 0 else []
    found = sum(1 for item in expected_ids if item in top)
    return found / len(expected_ids)


def reciprocal_rank(expected_ids, retrieved_ids):
    """1 divided by the position of the first expected chunk. 0.0 if none was found."""
    for position, item in enumerate(retrieved_ids, start=1):
        if item in expected_ids:
            return 1 / position
    return 0.0


def precision_at_k(expected_ids, retrieved_ids, k):
    """The share of the first k results that are expected. Always divides by k."""
    if k <= 0:
        return 0.0
    top = retrieved_ids[:k]
    good = sum(1 for item in top if item in expected_ids)
    return good / k


# Three retrievers with the SAME signature, so they can be compared on the same cases.
def vector_retriever(collection, question, k, embed):
    return search(collection, question, k=k, embed=embed)


def keyword_retriever(collection, question, k, embed):
    return keyword_search(collection, question, k=k)


def hybrid_retriever(collection, question, k, embed):
    return retrieve(collection, question, k=k, embed=embed)


RETRIEVERS = {"vector": vector_retriever, "keyword": keyword_retriever, "hybrid": hybrid_retriever}


def evaluate_retrieval(retriever, collection, cases, k=5, embed=embed_texts):
    """Run every case and average the scores.

    cases: [{"question": str, "expected": [chunk ids]}]. Returns n, recall, precision, mrr and
    "misses": the questions that had expected chunks but found none of them.
    """
    if not cases:
        return {"n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": []}
    recall_total = 0.0
    precision_total = 0.0
    rr_total = 0.0
    misses = []
    for case in cases:
        hits = retriever(collection, case["question"], k, embed)
        retrieved = [hit["id"] for hit in hits]
        recall = recall_at_k(case["expected"], retrieved, k)
        recall_total += recall
        precision_total += precision_at_k(case["expected"], retrieved, k)
        rr_total += reciprocal_rank(case["expected"], retrieved)
        if case["expected"] and recall == 0.0:
            misses.append(case["question"])
    n = len(cases)
    return {
        "n": n,
        "recall": round(recall_total / n, 4),
        "precision": round(precision_total / n, 4),
        "mrr": round(rr_total / n, 4),
        "misses": misses,
    }


def load_cases(path):
    """The golden set: a JSON list of {"question", "expected"}. A bad file gives a clear error."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("the golden file must hold a JSON list")
    for i, case in enumerate(data):
        if not isinstance(case, dict) or "question" not in case or not isinstance(case.get("expected"), list):
            raise ValueError(f"case {i} needs a question and an expected list")
    return data


def compare_retrievers(collection, cases, k=5, embed=embed_texts):
    """Evaluate vector, keyword and hybrid on the same cases. Returns {name: result}."""
    return {name: evaluate_retrieval(fn, collection, cases, k, embed) for name, fn in RETRIEVERS.items()}
```

Read it in parts:

1. **`recall_at_k`**: of the chunks that should be found, how many are in the first `k`? It answers "did we find it?". If a question has no expected chunk, nothing can be missed, so the score is `1.0`.
2. **`reciprocal_rank`**: `1 / position` of the first right chunk. Position 1 gives 1.0, position 2 gives 0.5, not found gives 0. The average over all questions is **MRR**. It rewards putting the right chunk **high**.
3. **`precision_at_k`**: of the `k` results, how many are right? It always divides by `k`: three slots with one right chunk is 0.33, even if only one result came back. It answers "how much noise?".
4. **Three retrievers, one signature.** `(collection, question, k, embed)`. The keyword one ignores `embed`. Because the shape is the same, `evaluate_retrieval` does not care which search it scores. Passing a function as an argument (the same trick as `score_fn` in step 14) is what makes the comparison easy.
5. **`evaluate_retrieval`** runs every case and averages. `misses` lists the questions that had expected chunks and found **none**. Read that list first: those are the cases to fix.
6. **`load_cases`** checks the file and gives a clear error. A broken golden file that silently scores 0 wastes an afternoon.
7. **`compare_retrievers`** scores vector, keyword and hybrid on the same cases. Hybrid should not be worse than the better of the two. If it is, something is wrong.

### 2. The golden set: `evals/golden.json`

Make an `evals` folder and write 15 to 30 real questions, with the chunk ids that answer them. Find the ids with:

```bash
uv run python -m copilot.ingest_cli docs
```

Start with this shape:

```json
[
  {"question": "How do I delete a task?", "expected": ["tasks.md:2"]},
  {"question": "What does error 429 mean?", "expected": ["errors.md:1"]},
  {"question": "What is the price of the moon?", "expected": []}
]
```

Include a question with `"expected": []` (the docs have no answer). Those cases matter for the failure report from step 17 and for the judge in step 19.

A warning: chunk ids contain a position (`tasks.md:2`). If you edit a doc or change `max_chars`, ids can shift, and the golden set must be updated. That is a real cost of golden sets. Keep them small and in version control.

### 3. Print the table: `copilot/eval_cli.py`

```python
"""Score the search on your golden questions. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.eval_cli evals/golden.json
"""

import sys

from copilot.evals import compare_retrievers, load_cases
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "evals/golden.json"
    cases = load_cases(path)
    results = compare_retrievers(open_collection(DB_PATH), cases, k=3)
    print(f"{'retriever':<10} {'recall@3':>9} {'precision@3':>12} {'mrr':>6}")
    for name, result in results.items():
        print(f"{name:<10} {result['recall']:>9} {result['precision']:>12} {result['mrr']:>6}")
    for name, result in results.items():
        if result["misses"]:
            print(f"\n{name} missed: " + "; ".join(result["misses"]))


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.docs_cli sync docs
uv run python -m copilot.eval_cli evals/golden.json
```

You see three rows: vector, keyword, hybrid. Now change one thing (for example `max_chars` in `sync_folder`, or `k`), sync, and run it again. Write the numbers in your notes. This is how real teams tune RAG.

### 4. Commit

```bash
git add -A && git commit -m "Add a golden set and retrieval metrics"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 17)
│   ├── evals.py
│   └── eval_cli.py
├── evals/
│   └── golden.json
├── docs/
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `recall_at_k` (partial recall, empty expected, `k=0`), `reciprocal_rank` (position, first of several, not found), `precision_at_k` (divides by `k`), `evaluate_retrieval` (empty cases, averages, `misses`), the three retrievers (keyword finds an exact number, misses a synonym, vector finds the synonym), `compare_retrievers` (hybrid is never worse than the best single one on the test data) and `load_cases` (a bad file raises `ValueError`). Steps 1 to 17 must keep working.
