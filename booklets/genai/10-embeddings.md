# 10. Embeddings and similarity

A computer can compare numbers easily, but "meaning" is hard. **Embeddings** are the trick that turns meaning into numbers, so that a program can answer "how similar are these two texts?". Everything in search and RAG stands on this chapter.

## The idea: a map of meaning

An **embedding** is a list of numbers (a **vector**) that represents a piece of text. An **embedding model** produces it. The key property: **texts with similar meaning get vectors that are close together.**

Think of a map. Cities that are near each other in real life are near on the map. An embedding model draws a map where *meanings* are the places. "refund my money" and "I want my payment back" land next to each other, even though they share no words. "weather in Pune" lands far away.

@@ grid 3 | Figure 10.1: a toy 2-D map of meaning (real ones have hundreds of dimensions).
"refund my money"|close to the next one|green
"I want my payment back"|close to the one before|green
"weather in Pune"|far from both|gray
@@ end

Real embedding vectors have many **dimensions**, commonly 384, 768, 1024 or 1536 numbers per text. You never read them. You only compare them.

## Why not just search for words?

Keyword search matches **exact words**. A user types "cancel subscription" and the page says "end your plan". Zero shared words, no match. Embeddings match by **meaning**, so this works. But embeddings are weaker with exact things like error codes and names, which is why chapter 13 combines both.

## Measuring "close"

Three common ways to compare two vectors `a` and `b`:

| Measure | Idea | Good for |
| --- | --- | --- |
| **Cosine similarity** | the **angle** between them: 1 means same direction, 0 unrelated, -1 opposite | text (the usual choice) |
| **Dot product** | multiply and add; also depends on length | when vectors are already normalised |
| **Euclidean (L2) distance** | straight-line distance; smaller means closer | some models and indexes |

Cosine similarity is the main one. Its formula: the dot product divided by the product of the lengths. With numpy (`uv add numpy`):

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
b = np.array([2.0, 4.0, 6.0])
c = np.array([-1.0, 0.0, 0.0])

def cosine(x, y):
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))

print(round(cosine(a, b), 3), round(cosine(a, c), 3))
# -> 1.0 -0.267
print(float(a @ b), round(float(np.linalg.norm(a - b)), 3))
# -> 28.0 3.742
```

Reading the results: `b` is just `a` doubled, so they point the **same way**, cosine 1.0, even though `b` is longer (the distance is 3.742, not 0). `c` points a bit the opposite way, so it is negative. That is why cosine is good for meaning: it ignores **how long** the vector is and looks only at **direction**.

`@` is numpy's dot product. `np.linalg.norm` is the length of a vector.

### Normalise once, then dot product is cosine

If you **scale every vector to length 1** (normalise), the dot product *equals* the cosine similarity, and it is much faster. Many embedding models already return normalised vectors, and many vector databases normalise for you.

## Searching many texts at once

For a question vector and a matrix of document vectors, you can score **all** documents with a single matrix multiplication:

```python
M = np.array([[1, 0], [0.9, 0.1], [0, 1], [-1, 0]], dtype=float)   # 4 documents
q = np.array([1, 0.05])                                              # the query

M_normal = M / np.linalg.norm(M, axis=1, keepdims=True)
q_normal = q / np.linalg.norm(q)
scores = M_normal @ q_normal
print(np.round(scores, 3))
# -> [ 0.999  0.998  0.05  -0.999]
print(np.argsort(-scores)[:2])
# -> [0 1]
```

Step by step: normalise every row, normalise the query, multiply (one score per document), then `argsort(-scores)` lists document numbers from highest score to lowest. `[:2]` takes the **top 2**. This is the whole idea of **semantic search**, and it needs only a few lines.

## A toy embedder to see it work

A real embedder needs a model. To feel the full pipeline with no download, here is a fake one that just counts a few chosen words. It is **not** semantic, but the plumbing is identical:

```python
VOCAB = ["refund", "money", "back", "days", "password", "reset", "login", "shipping", "order", "track"]

def embed(text):
    text = text.lower()
    v = np.array([text.count(w) for w in VOCAB], dtype=float)
    n = np.linalg.norm(v)
    return v / n if n else v

docs = [
    "You can get your money back: refund within 30 days",
    "Reset your password on the login page",
    "Track your order after shipping",
]
doc_vectors = np.array([embed(d) for d in docs])
query = embed("how do I reset my password to login")
print(np.round(doc_vectors @ query, 2))
# -> [0. 1. 0.]
```

The second document scores 1.0, so it is the answer. A real embedder would also score "I forgot my sign-in" high, even with no shared word. That is the difference between counting words and capturing meaning.

## A real embedding model

Where do real embeddings come from? Two options:

1. **An API** (OpenAI, Cohere, Voyage and others): you send text and get vectors back. Simple, but costs money and sends your text out.
2. **A local model** (such as `BAAI/bge-small-en-v1.5`, 384 dimensions, with the `fastembed` or `sentence-transformers` libraries): free to run, private, and fast enough on a laptop.

```python
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")
vectors = list(model.embed(["refund my money", "I want my payment back"]))
print(len(vectors[0]))
# -> 384
```

(This snippet was not run here, because it downloads a model on first use. The 384 is the documented size for this model.)

**Golden rules of embeddings:**

- Use the **same model** for documents and for queries. Vectors from different models are not comparable.
- Different models have different dimensions. If you change the model, **re-embed everything**.
- Embeddings capture meaning in the **language** of the model. For other languages use a multilingual model.
- Long texts are cut at the model's input limit. That is one reason we **chunk** (chapter 11).

## Where embeddings are used

Semantic search, RAG, recommendations ("similar items"), duplicate detection, clustering, classification by nearest example, and long-term memory for agents.

::: {.box .checkpoint}
**Checkpoint:** you can explain why cosine ignores vector length, and write the code that returns the top 3 most similar documents.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Embedding documents with one model and queries with another.
- Comparing raw dot products of un-normalised vectors and expecting cosine.
- Changing the embedding model and keeping old vectors.
- Expecting embeddings to be good at exact matches like IDs and error codes.
- Embedding a whole book as one vector.
- Reading the individual numbers in a vector as if they had meaning.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is an embedding?** A fixed-length vector that represents a text so that similar meanings give nearby vectors.

**Q: Cosine similarity vs dot product vs L2?** Cosine compares direction only and ignores length. Dot product also depends on length (equal to cosine for normalised vectors). L2 is straight-line distance.

**Q: Why normalise vectors?** Then dot product equals cosine, which is faster, and scores are comparable.

**Q: Why must queries and documents use the same embedding model?** Different models map text into different spaces, so their vectors cannot be compared.

**Q: What are the limits of embedding search?** Weak on exact terms, codes and rare names, and sensitive to chunking and the model's language coverage.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Compute the cosine of `[1, 0]` and `[0, 1]`, of `[1, 1]` and `[2, 2]`, and of `[1, 0]` and `[-1, 0]`.
2. Write `top_k(query_vec, matrix, k)` that returns the indexes of the k best rows.
3. Extend the toy `VOCAB` with five words from your own topic and search five of your own documents.
4. Show that two vectors with different lengths but the same direction have cosine 1, but a non-zero L2 distance.
5. If an embedding has 384 dimensions and stores each number in 4 bytes, how many megabytes do 100,000 vectors need?
6. **Think:** why does a search system built with one embedding model need a full re-index when you switch models?
:::
