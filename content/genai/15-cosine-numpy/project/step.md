# Step 8 — Search by meaning

So far Copilot answers from text you paste in. Now it learns to **find** the right text. In this step you build the first version of search: turn texts into vectors, score them against the question, and take the best ones. Everything stays in memory. A vector database comes in step 10.

You need two new libraries. In your project folder:

```bash
uv add numpy fastembed
```

`fastembed` runs a small embedding model on your own computer. The first run downloads about 130 MB. After that it works offline.

### 1. Embeddings: `copilot/embed.py`

```python
"""Turn texts into vectors with a local model (no API key, no network after the first download)."""

MODEL_NAME = "BAAI/bge-small-en-v1.5"

_models = {}


def embed_texts(texts, model_name=MODEL_NAME):
    """Embed a list of texts. Returns one list of floats per text.

    The model is loaded the first time and kept, so later calls are fast.
    """
    if not texts:
        return []
    if model_name not in _models:
        from fastembed import TextEmbedding   # imported here so the rest of Copilot works without it

        _models[model_name] = TextEmbedding(model_name)
    return [vector.tolist() for vector in _models[model_name].embed(texts)]
```

Two best practices here:

- **Load the model once.** Loading takes seconds. The `_models` dictionary remembers it.
- **Import inside the function.** The heavy library is only loaded when you really embed. Tests and other modules stay fast.

### 2. Maths: `copilot/similarity.py`

Pure functions. No model, no network. These are the ones you wrote in the exercises of lesson 15.

```python
"""Compare vectors. Pure functions, no model calls."""

import numpy as np


def cosine_similarity(a, b):
    """Cosine of the angle between two vectors. A zero vector gives 0.0."""
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    x = np.array(a, dtype=float)
    y = np.array(b, dtype=float)
    length_x = np.linalg.norm(x)
    length_y = np.linalg.norm(y)
    if length_x == 0 or length_y == 0:
        return 0.0
    return float(np.dot(x, y) / (length_x * length_y))


def cosine_scores(query_vector, doc_vectors):
    """One cosine score per document vector. A zero vector scores 0.0."""
    if len(doc_vectors) == 0:
        return []
    docs = np.array(doc_vectors, dtype=float)
    q = np.array(query_vector, dtype=float)
    lengths = np.linalg.norm(docs, axis=1) * np.linalg.norm(q)
    dots = docs @ q
    scores = np.zeros(len(docs))
    nonzero = lengths != 0
    scores[nonzero] = dots[nonzero] / lengths[nonzero]
    return [float(s) for s in scores]


def top_k(query_vector, doc_vectors, k):
    """The k best documents as (index, score) pairs, best first. Ties: lower index first."""
    if k <= 0 or len(doc_vectors) == 0:
        return []
    scores = cosine_scores(query_vector, doc_vectors)
    order = np.argsort(-np.array(scores), kind="stable")[:k]
    return [(int(i), scores[i]) for i in order]
```

### 3. Search: `copilot/search.py`

```python
"""First version of search: embed everything, score, take the best k. In memory only."""

from copilot.embed import embed_texts
from copilot.similarity import top_k


def search_texts(query, texts, k=3, embed=embed_texts):
    """Find the k texts closest in meaning to the query.

    Returns a list of {"index", "text", "score"}, best first.
    `embed` takes a list of texts and returns a list of vectors. Tests pass a fake one.
    """
    if k <= 0 or not texts:
        return []
    doc_vectors = embed(texts)
    query_vector = embed([query])[0]
    return [
        {"index": index, "text": texts[index], "score": score}
        for index, score in top_k(query_vector, doc_vectors, k)
    ]
```

Notice `embed=embed_texts`. It is a **default argument that is a function**. Real code uses the real model. A test passes a tiny fake, so the test needs no download and runs in milliseconds. This is the same idea as passing a fake `client` in step 1.

Why do we return dictionaries with `index`, `text` and `score` and not just text? Later steps need to know **where** a result came from (its source file, its heading). A dictionary can grow. A bare string cannot.

### 4. Try it for real

Add `copilot/search_cli.py`:

```python
"""Try the search on a few built-in sentences: python -m copilot.search_cli "your question"."""

import sys

from copilot.search import search_texts

SAMPLE = [
    "Use the DELETE endpoint to remove a task.",
    "Send a POST request to create a new task.",
    "Log in with your email and password to get a token.",
    "The weather today is sunny.",
]


def main():
    question = " ".join(sys.argv[1:]) or "How do I get rid of a todo item?"
    for hit in search_texts(question, SAMPLE, k=3):
        print(f"{hit['score']:.3f}  {hit['text']}")


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.search_cli "How do I get rid of a todo item?"
```

The DELETE sentence should come first, even though the question shares almost no words with it. That is meaning-based search. Try a few of your own questions and look at the scores.

### 5. Commit

```bash
git add -A && git commit -m "Add embeddings and cosine search"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── cli.py
│   ├── embed.py
│   ├── llm.py
│   ├── memory.py
│   ├── prompts.py
│   ├── qa.py
│   ├── schemas.py
│   ├── search.py
│   ├── search_cli.py
│   ├── similarity.py
│   ├── spec_tools.py
│   ├── summary.py
│   └── tools.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `cosine_similarity` (including zero vectors and different lengths), `cosine_scores`, `top_k` (ties, `k` too big, `k <= 0`), and `search_texts` with a fake `embed` (one batch call for the texts, one for the query). Steps 1 to 7 must keep working. The tests never download the model.
