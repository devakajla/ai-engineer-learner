---
title: Cosine similarity with numpy
summary: Compare embeddings with cosine similarity, use numpy to score many documents at once, and pick the top k matches.
plan_ids: []
---

Last lesson gave you two ways to compare vectors: dot product and Euclidean distance. For text, almost everyone uses a third one: **cosine similarity**. In this lesson you learn what it is, why it fits text, and how to do it for thousands of documents in one line with **numpy**.

Then you build your first real search: question in, best matching texts out.

## Why not just the dot product?

Look at two vectors that point the same way, but one is longer:

```python
a = [1, 1]
b = [10, 10]
```

They point in the **same direction**. For text, same direction means same meaning. But the dot product is `1*10 + 1*10 = 20`, and for a short vector it would be smaller. The **length** of a vector changes the score, and length is usually not what we care about.

Cosine similarity ignores length. It only looks at the **direction**.

## What cosine similarity says

It gives a number between **-1 and 1**:

- `1` means the same direction (very similar).
- `0` means unrelated (a right angle).
- `-1` means the opposite direction.

For text embeddings, real scores are usually between about 0 and 1. A bigger number means "more similar". This is the opposite of a distance, where smaller means closer.

The formula:

```
cosine(a, b) = dot(a, b) / (length(a) * length(b))
```

The **length** of a vector is `sqrt(x1**2 + x2**2 + ...)`. You saw this idea in lesson 14: the distance from the zero vector.

By hand, with `a = [1, 0]` and `b = [1, 1]`:

1. `dot(a, b) = 1*1 + 0*1 = 1`
2. `length(a) = sqrt(1) = 1`
3. `length(b) = sqrt(1 + 1) = sqrt(2) = 1.414...`
4. `cosine = 1 / (1 * 1.414...) = 0.707...`

So these two vectors are fairly similar (they are 45 degrees apart).

> Why the name "cosine"? The number equals the cosine of the angle between the two vectors. You do not need trigonometry. Remember: **1 is the same direction, 0 is unrelated.**

## numpy in five minutes

**numpy** is a library for fast maths on lists of numbers. Real embeddings have hundreds of numbers, and you will compare them with thousands of documents. Python loops would be slow. numpy does the loop in fast compiled code.

It is already installed in the Learner project. In your own project, add it with `uv add numpy`.

The convention is to import it as `np`:

```python
import numpy as np

a = np.array([1, 2, 3])        # a numpy array (like a list, built for maths)
print(a)                       # -> [1 2 3]
print(a * 2)                   # -> [2 4 6]       (works on every item at once)
print(a + np.array([10, 10, 10]))   # -> [11 12 13]
```

An array does the maths on **all items at once**. No loop.

Three tools you need:

```python
a = np.array([1.0, 2.0, 2.0])
b = np.array([2.0, 0.0, 1.0])

print(np.dot(a, b))            # -> 4.0        (1*2 + 2*0 + 2*1)
print(np.linalg.norm(a))       # -> 3.0        (the length: sqrt(1 + 4 + 4))
print(a.shape)                 # -> (3,)       (3 numbers)
```

- `np.dot(a, b)` is the dot product.
- `np.linalg.norm(a)` is the length of a vector. ("norm" is the maths word for length.)
- `.shape` tells you the size.

The results are numpy numbers (`np.float64`), which behave like normal floats. Wrap with `float(...)` when you want a plain Python number, for example to return from a function or to print neatly.

### Step by step: the length of a vector, and a vector of length 1

A different small job, same style as the cosine function you will write.

Goal: write `unit(v)` that scales a vector so its length is 1. Steps:

1. Turn the list into an array with `np.array(v, dtype=float)`.
2. Find its length with `np.linalg.norm(...)`.
3. **Guard:** if the length is `0`, you cannot divide. Return the zeros as they are.
4. Otherwise divide the array by the length.

```python
def unit(v):
    arr = np.array(v, dtype=float)
    length = np.linalg.norm(arr)
    if length == 0:
        return arr
    return arr / length

print(unit([3, 4]))    # -> [0.6 0.8]
print(unit([0, 0]))    # -> [0. 0.]
```

The guard in step 3 matters. A zero vector has no direction. Dividing by zero would give `nan` ("not a number") and spoil everything after it. Cosine similarity needs the same guard: when either vector has length 0, return `0.0`.

The first exercise asks for the cosine function. It follows the same shape: arrays, norms, a guard, then the formula.

## Scoring many documents at once

Now the useful part. You have one question vector and a **matrix** of document vectors. A matrix is a 2D array: one row per document.

```python
docs = np.array([
    [1.0, 0.0],     # doc 0
    [0.0, 1.0],     # doc 1
    [1.0, 1.0],     # doc 2
])
query = np.array([1.0, 0.0])

print(docs.shape)          # -> (3, 2)    3 rows, 2 columns
print(docs @ query)        # -> [1. 0. 1.]   the dot product of every row with the query
```

`matrix @ vector` takes the dot product of **every row** with the vector, in one line. That is 3 dot products (or 10,000) without a loop.

To make those dot products into cosine scores, divide by the lengths:

```python
doc_lengths = np.linalg.norm(docs, axis=1)     # one length per row
print(doc_lengths)                             # -> [1.         1.         1.41421356]
scores = (docs @ query) / (doc_lengths * np.linalg.norm(query))
print(scores)                                  # -> [1.         0.         0.70710678]
```

`axis=1` means "work along each row". Doc 0 has the same direction as the query (1.0). Doc 1 is unrelated (0.0). Doc 2 is in between (0.707).

> Shortcut used in practice: if every vector is **normalized** (length 1) once, when stored, then the cosine is just the dot product. Many embedding models already return normalized vectors, and vector databases can normalize for you. That is why "dot product" and "cosine" are often used as the same thing. If you are not sure, compute the full formula. It is always correct.

## Picking the top k

You have a score for each document. You want the best `k`. This is called **top-k**.

```python
scores = np.array([0.2, 0.9, 0.5, 0.7])
order = np.argsort(-scores)       # indexes, best score first
print(order)                      # -> [1 3 2 0]
print(order[:2])                  # -> [1 3]      the top 2
```

- `np.argsort(x)` gives the **indexes** that would sort `x` from small to big.
- The minus sign flips it, so the biggest comes first.
- A slice `[:k]` takes the first `k`.

If you ask for more than there are, the slice just returns everything. That is safe.

Ties: when two documents have the same score, you want a steady, predictable order. Use `np.argsort(-scores, kind="stable")`. A stable sort keeps equal items in their original order, so the lower index wins.

Now turn the indexes back into texts:

```python
texts = ["intro", "delete a task", "list tasks", "login"]
for i in order[:2]:
    print(texts[i], float(scores[i]))
# -> delete a task 0.9
# -> login 0.7
```

## Your first search

Put it all together. A search function does five things:

1. Embed all the documents (one call, a batch).
2. Embed the question.
3. Score every document against the question.
4. Pick the top `k`.
5. Return the texts with their scores.

In pseudo-code:

```python
def search_texts(embed, query, texts, k=3):
    doc_vectors = embed(texts)           # one list of numbers per text
    query_vector = embed([query])[0]     # embed returns a list, take the first
    ...
```

The `embed` argument is a function that takes a **list of texts** and returns a **list of vectors**. That is exactly what `fastembed` does, and it is easy to fake in tests. (Passing a function in is the idea from lesson 14.)

Why embed documents in one call? Models are much faster in batches. One call for 100 texts is far quicker than 100 calls.

> This version embeds all documents on every search. That is fine for learning and for tiny data. In lesson 17 a vector database stores the vectors once, so you do not repeat the work.

## When nothing matches: a minimum score

A search always returns its top results, even when all of them are poor. If you search for *"pizza"* in API docs, you still get 3 results, and they are not about pizza.

The fix is a **minimum score**. Keep only the results whose score is high enough. If nothing is left, the app knows the docs have no answer, and it can say so. This will matter a lot in RAG (Level 4).

Let's practise the pattern with a different example: keep the exam marks that pass.

```python
marks = [("Asha", 82), ("Ravi", 35), ("Mina", 60)]
passed = [(name, mark) for name, mark in marks if mark >= 40]
print(passed)   # -> [('Asha', 82), ('Mina', 60)]
```

The `if` at the end of a list comprehension filters. In the fourth exercise you filter `(text, score)` pairs the same way.

> What is a good minimum score? There is no universal number. It depends on the embedding model. Try your real questions, look at the scores of good and bad matches, and pick a value between them.

## Try it live

1. Embed 6 doc sentences and 3 questions (two on topic, one off topic like *"best pizza in Delhi"*) with `fastembed`. Print the top score for each question.
2. Write the scores down. Is there a clear gap between on-topic and off-topic?
3. Choose a `min_score` in the gap and test it.

## A little deeper

- **Cosine distance** is `1 - cosine similarity`. Some libraries (Chroma, pgvector) report **distance**, where small is good. Know which one you are looking at. Lesson 17 shows the Chroma version.
- **Why the `@` operator?** It is Python's matrix multiplication symbol. `docs @ query` multiplies a matrix by a vector. You can also write `np.dot(docs, query)`.
- **Float noise.** Cosine of a vector with itself may come out as `0.9999999999999999` or `1.0000000000000002`. Never test equality with `==` on floats. Use `round(x, 6)` or `pytest.approx`.
- **Memory and speed.** 100,000 vectors of 384 float32 numbers is about 150 MB. A `matrix @ vector` over that takes a few milliseconds. For many millions of vectors, you need an **approximate** index (lesson 19).
- **float32 vs float64.** numpy uses 64-bit floats by default. Embedding libraries often return 32-bit floats, which take half the memory and are accurate enough for search.
- **Top-k faster:** `np.argpartition` finds the top k without sorting everything. For small data the full sort is fine.
- **Not just similarity.** The best match can still be a bad one. Real systems use a minimum score (a threshold) so that "no good answer" is possible. Level 4 returns to this.

## Common mistakes

- Dividing by zero for a zero vector, and getting `nan`.
- Comparing vectors with different lengths. numpy raises an error for mismatched shapes, which is good. Add your own clear message.
- Sorting scores the wrong way: `argsort` goes **small to big**. Use `-scores`.
- Mixing up similarity (bigger is better) and distance (smaller is better).
- Checking float equality with `==`.
- Embedding the documents again for every question.
- Forgetting that `embed` takes a **list**. `embed("text")` is wrong. `embed(["text"])[0]` is right.

## Interview corner

**Why cosine similarity and not Euclidean distance for text embeddings?**
Cosine looks at direction, not length, and direction carries the meaning. For normalized vectors, ranking by cosine, dot product and Euclidean distance gives the same order. Cosine is the usual default.

**What is the range of cosine similarity?**
-1 to 1. For text embeddings in practice, mostly 0 to 1. Higher is more similar.

**How do you find the top k results fast?**
Score everything with one matrix multiplication, then take the top k indexes with `argsort` or `argpartition`. For huge data, use an approximate index.

**What if the query vector is all zeros?**
The cosine is undefined (division by zero). Return 0 or skip it. Never let `nan` flow into your ranking.

## Summary

- Cosine similarity = dot product divided by the two lengths. It compares direction. 1 is the same, 0 is unrelated.
- numpy: `np.array`, `np.dot`, `np.linalg.norm`, `matrix @ vector`, `np.argsort(-scores)`.
- Guard against zero length vectors.
- Top-k: sort the indexes by score and slice `[:k]`. Use a stable sort so ties are predictable.
- A search function: embed documents (batch), embed the query, score, take top k, return texts with scores.
- Project: step 8 adds `copilot/embed.py`, `copilot/similarity.py` and `copilot/search.py`.
- Reference: `reference/genai-retrieval.md`.
