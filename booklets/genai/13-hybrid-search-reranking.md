# 13. Keyword search, hybrid search and reranking

Embedding search finds **meaning**. But it can fail on exact things: an error code like `E404`, a product name, a rare word. Old-fashioned **keyword search** is great at those. The strongest systems use **both**, then re-order the best candidates with a smarter model. This chapter builds that.

## Where each one wins

| Query | Keyword search | Embedding search |
| --- | --- | --- |
| "error E404" | finds the exact code | may return general "not found" pages |
| "how do I get my money back" | misses "refund" pages | finds them |
| "iPhone 15 Pro Max case" | exact model names | may mix in other phones |

Neither is better. They are **complementary**.

## BM25: the keyword scorer

**BM25** is the classic scoring formula inside search engines (Elasticsearch, Lucene). For each query word in a document, it gives points by:

- **Term frequency (TF):** how often the word appears in the document. More is better, but with **diminishing returns** (the 10th mention adds little).
- **Inverse document frequency (IDF):** how **rare** the word is across all documents. "the" is in everything and is worth nothing. "E404" is rare, so worth a lot.
- **Length normalisation:** a match in a short document counts more than in a very long one.

You can implement it in a few lines. This version was run:

```python
import math, re

def tokenize(text):
    return re.findall(r"\w+", text.lower())

def bm25_scores(query, docs, k1=1.5, b=0.75):
    tokens = [tokenize(d) for d in docs]
    n = len(tokens)
    avg_len = sum(len(t) for t in tokens) / n
    doc_freq = {}
    for t in tokens:
        for word in set(t):
            doc_freq[word] = doc_freq.get(word, 0) + 1

    scores = []
    for t in tokens:
        score = 0.0
        for word in tokenize(query):
            if word not in doc_freq:
                continue
            idf = math.log(1 + (n - doc_freq[word] + 0.5) / (doc_freq[word] + 0.5))
            tf = t.count(word)
            score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(t) / avg_len))
        scores.append(round(score, 3))
    return scores

corpus = [
    "the cat sat on the mat",
    "the dog chased the cat",
    "error code E404 not found",
    "dogs and cats",
]
print(bm25_scores("E404", corpus))
# -> [0.0, 0.0, 1.176, 0.0]
print(bm25_scores("cat", corpus))
# -> [0.62, 0.677, 0.0, 0.0]
```

Reading the output: the rare code `E404` found only document 3. For `cat`, documents 1 and 2 score, with document 2 slightly higher because it is shorter (length normalisation) even though both contain the word once. Document 4 has `cats`, which is a different word, so **BM25 knows nothing about meaning or word forms** (unless you add stemming). `k1` and `b` are tuning knobs; 1.5 and 0.75 are the usual defaults. In real projects use a library (`rank_bm25`), or a search engine.

## Hybrid search: use both lists

Run keyword search and vector search separately. You get two ranked lists. Now **merge** them. Problem: BM25 scores (such as 1.176) and cosine scores (such as 0.83) are on different scales, so adding them is meaningless.

### Reciprocal Rank Fusion (RRF)

RRF ignores the scores and uses only the **ranks**. A document gets `1 / (k + rank)` from each list it appears in, and the points are added. `k` is usually 60.

```python
def rrf(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for position, doc in enumerate(ranking, start=1):
            scores[doc] = scores.get(doc, 0) + 1 / (k + position)
    order = sorted(scores, key=scores.get, reverse=True)
    return order, {doc: round(s, 4) for doc, s in scores.items()}

keyword = ["a", "b", "c"]
vector = ["c", "a", "d"]
print(rrf([keyword, vector]))
# -> (['a', 'c', 'b', 'd'], {'a': 0.0325, 'b': 0.0161, 'c': 0.0323, 'd': 0.0159})
```

Why this is clever: `a` is first in one list and second in the other, `c` is third and first, `b` and `d` each appear in only one. Documents that **both** methods like rise to the top (`a` and `c`), and nothing needs tuning between the two score scales. RRF is simple, robust, and a very common default.

@@ flow | Figure 13.1: hybrid search.
Question|the user's text|blue -> Keyword search|BM25;exact terms|yellow -> Vector search|embeddings;meaning|green -> Merge (RRF)|one combined list|purple -> Top K|best chunks|blue
@@ end

Many databases can do this directly: Elasticsearch, Qdrant, Weaviate and Postgres (full-text search plus pgvector).

## Reranking: a second, smarter look

The first stage (vector or hybrid) must be **fast**, so it is rough. It is good at "these 50 are probably relevant". A **reranker** then reads the question **together with each candidate** and scores how well they match, more accurately, and re-orders the top.

Why is it more accurate? An embedding model compares two **separate** vectors that were made without seeing each other. A **cross-encoder** reranker reads the query and the passage **together**, so it can see how the words relate.

@@ flow | Figure 13.2: retrieve many, rerank, keep few.
Retrieve|top 50;fast and rough|blue -> Rerank|cross-encoder scores each pair;slower but accurate|yellow -> Keep|top 5;go into the prompt|green
@@ end

Options: a cross-encoder model (for example from `sentence-transformers`, or hosted rerank APIs from Cohere and others), or an LLM asked "rate this passage from 0 to 10 for the question". The cost is **extra latency**, and the benefit is often a clear gain in answer quality. Apply it only to the top 20 to 50, never to the whole corpus.

## Metrics to judge retrieval

How do you know a change helped? Use a test set of questions with the known correct chunks (chapter 16), and measure:

```python
relevant = {"a", "c"}
retrieved = ["a", "x", "c", "y"]

precision_at_3 = len([d for d in retrieved[:3] if d in relevant]) / 3
recall_at_4 = len([d for d in retrieved if d in relevant]) / len(relevant)
first_hit_rank = next(i for i, d in enumerate(retrieved, 1) if d in relevant)
print(round(precision_at_3, 2), recall_at_4, 1 / first_hit_rank)
# -> 0.67 1.0 1.0
```

- **precision@k:** of the top k results, how many are relevant (here 2 of 3).
- **recall@k:** of all relevant documents, how many did you find (both).
- **MRR** (mean reciprocal rank): average of `1 / rank of the first relevant result`. Here the first hit is rank 1, so 1.0.

::: {.box .checkpoint}
**Checkpoint:** you can explain why BM25 finds `E404` and embeddings may not, why RRF uses ranks, and why a reranker only sees the top candidates.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Adding BM25 scores and cosine scores directly.
- Reranking the whole corpus instead of the top candidates.
- Only using embeddings, and failing on IDs, codes and names.
- Never measuring, so "hybrid" is a guess.
- Retrieving too few candidates before reranking.
- Forgetting that BM25 sees words, not meaning (no synonyms).
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is BM25?** A keyword ranking function using term frequency (with saturation), inverse document frequency and document length normalisation.

**Q: Why hybrid search?** Keyword search finds exact terms and rare tokens. Vector search finds meaning. Combining them covers both failure modes.

**Q: What is reciprocal rank fusion?** A way to merge ranked lists by summing `1 / (k + rank)` for each document, ignoring raw scores.

**Q: Bi-encoder vs cross-encoder?** A bi-encoder embeds query and document separately (fast, used for retrieval). A cross-encoder reads them together (slower, more accurate, used for reranking).

**Q: What are recall@k and MRR?** Recall@k is the share of relevant documents found in the top k. MRR averages the reciprocal rank of the first relevant result.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Run `bm25_scores` for a word that appears in two documents of different lengths. Which scores higher and why?
2. Merge three rankings with `rrf`. Which document wins if it is second in all three?
3. Build a hybrid search over your six toy documents: BM25 plus the toy embedder plus RRF.
4. Write `recall_at_k(retrieved, relevant, k)` and `mrr(list_of_results)`.
5. Write a function that asks an LLM to rate passages from 0 to 10 and sorts them (use a fake client in a test).
6. **Think:** why do we rerank only the top candidates and not every chunk?
:::
