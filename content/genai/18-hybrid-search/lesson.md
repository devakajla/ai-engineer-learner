---
title: Keyword search (BM25) and hybrid search
summary: See where meaning-based search fails, learn how BM25 scores exact words, and combine both rankings with reciprocal rank fusion.
plan_ids: []
---

Vector search finds meaning. That is great, but it has a blind spot: **exact words**.

Ask your docs: "What does error 429 mean?" or "What is the `X-API-Key` header?" A vector search may return chunks about "errors in general" or "API headers in general", because the embedding blurs the exact code and the exact name. A good old **keyword search** finds the chunk that contains `429` immediately.

Real systems use **both**. This is called **hybrid search**, and it is one of the best upgrades you can make to a RAG system. It is also a very common interview topic.

## Vector search vs keyword search

| | Vector search | Keyword search |
| --- | --- | --- |
| Matches | meaning | exact words |
| Good at | "get rid of a todo" finds "delete a task" | `429`, `X-API-Key`, function names, rare words |
| Weak at | exact codes, names, numbers | synonyms, different wording |
| Needs a model | yes | no |

Neither is better. They fail in **different** places. Combine them and each covers the weakness of the other.

## Keyword search: from counting to BM25

The first idea: score a document by how many times the query words appear in it. That has two problems:

1. **Common words dominate.** "the" appears everywhere. A word that is in nearly every document says nothing.
2. **Long documents win.** A long document has more words, so more matches by chance.

**BM25** (Best Match 25) is the standard fix. It is the scoring behind Elasticsearch, OpenSearch and many other search tools. It uses three ideas.

### Idea 1: term frequency (TF), with a ceiling

`tf` is how many times the word appears in the document. More is better, but **with diminishing returns**: the 10th "delete" adds much less than the 1st. A parameter `k1` (usually 1.2 to 2) controls how fast the gain flattens.

### Idea 2: inverse document frequency (IDF)

A word that appears in **few** documents is rare, so it is informative. A word in **every** document is useless.

```
df  = number of documents that contain the word
idf = ln(1 + (N - df + 0.5) / (df + 0.5))        N = number of documents
```

`ln` is the natural logarithm: `math.log` in Python. Rare words get a big idf, common words a small one.

### Idea 3: length normalization

A document that is longer than average gets a small penalty, a shorter one a small bonus. A parameter `b` (usually 0.75) sets how strong. `b = 0` turns it off.

### The formula

For each query word, add this to the document's score:

```
idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_length / avg_doc_length))
```

Do not memorize it. Read it as: **rare word** (idf) times **how often it appears** (tf, flattened), **adjusted for length**.

### Step by step: document frequency and idf

You will need these two pieces in the exercise. Here they are for a different job, with letters, so you can see the pattern.

Goal: `letter_idf(letter, words)` where `words` is a list of words. `df` is the number of words that contain the letter.

1. Count `df`: loop over the words, add 1 when the letter is in the word.
2. `N` is `len(words)`.
3. Return `math.log(1 + (N - df + 0.5) / (df + 0.5))`.

```python
import math

def letter_idf(letter, words):
    df = 0
    for word in words:
        if letter in word:
            df += 1
    n = len(words)
    return math.log(1 + (n - df + 0.5) / (df + 0.5))

words = ["tea", "eat", "ate", "zoo"]
print(round(letter_idf("e", words), 4))   # -> 0.3567   (3 of 4 words: common, low idf)
print(round(letter_idf("z", words), 4))   # -> 1.204    (1 of 4 words: rare, high idf)
print(round(letter_idf("q", words), 4))   # -> 2.3026   (0 of 4 words: never seen)
```

Rare is worth more. In BM25 a word the document does not contain adds nothing (its `tf` is 0), so the "never seen" case never changes a score. A word counts once per document for `df`, however many times it appears there.

### Tokens for keyword search

BM25 works on **words**, so first you cut the text into a list of lowercase words (tokens). You did a version of this in lesson 14 (`toy_embed`). Real search tools use smarter tokenizers. Ours:

1. Make the text lowercase and split on whitespace.
2. Strip punctuation from both ends of each word: `.,;:!?()"'` and the backtick.
3. Drop empty pieces.

```python
print("Use `DELETE /tasks/{id}`.".lower().split())
# -> ['use', '`delete', '/tasks/{id}`.']
```

After stripping the ends: `['use', 'delete', '/tasks/{id}']`. Notice that the inside of a word is left alone, so names like `x-api-key` and numbers like `429` stay whole. That is what makes keyword search good at exact terms.

## Why you cannot just add the two scores

Cosine scores live between 0 and 1. BM25 scores can be 0.3 or 14.7. They are on **different scales**, so adding them lets one side win by accident. Two ways out:

1. **Normalize** both (for example to 0..1) and add them with weights.
2. **Ignore the scores, use the ranks.** Reciprocal Rank Fusion. This is the popular one, because it needs no tuning.

## Reciprocal Rank Fusion (RRF)

Each search gives a ranked list: first place, second place, and so on. For each item, RRF adds up `1 / (k + rank)` over every list the item appears in. The rank starts at 1. `k` is a constant, usually 60.

```python
vector_ranking  = ["a", "b", "c"]
keyword_ranking = ["c", "a", "d"]
k = 60

# a: 1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03252
# b: 1/(60+2)            = 0.01613
# c: 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226
# d: 1/(60+3)            = 0.01587
```

Best first: `a` (0.03252), `c` (0.03226), `b` (0.01613), `d` (0.01587).

Look at what happened: `a` and `c` are in **both** lists, so they beat `b` and `d`, which are only in one. An item that both methods like rises to the top. That is the whole point.

The constant `k` softens the difference between rank 1 and rank 2. With a big `k`, ranks matter less.

## The hybrid pipeline

```
question
  ├─► vector search  ─► top 20 ─┐
  └─► keyword search ─► top 20 ─┴─► RRF ─► top 5 ─► (the LLM, in Level 4)
```

Take **more** candidates from each side (say 20) than you finally need (say 5), then fuse and cut. If each side returned only 5, the fusion would have nothing to work with.

## The full hybrid search in one function

You now have all parts: BM25 for exact words, vectors for meaning, and RRF to merge. The final function does three things: make two rankings, drop the documents with no keyword match from the keyword ranking, and fuse.

Let's practise the "drop the zeros, then rank" step with a different example: rank players by a score, but only players who scored.

```python
def rank_scorers(scores):
    order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
    return [i for i in order if scores[i] > 0]

rank_scorers([0, 5, 3, 0])   # -> [1, 2]
```

`range(len(scores))` gives the indexes 0, 1, 2, 3. `key=scores.__getitem__` sorts the indexes by their score (it is the same as `scores[i]`). Players with 0 are left out, as a document with no keyword match must be. The fourth exercise uses this idea twice and fuses the two lists.

## Try it live

1. Make 10 short doc sentences. Include one with an error code like `E1042` and one that uses other words for the same idea as a question.
2. Search with a vector-only method, BM25-only, and hybrid for: an exact code, a question in different words, and a mix. Print the top 3 of each.
3. Which method wins for which query? Write it down. This is why hybrid is the default in real systems.

## A little deeper

- **BM25 vs TF-IDF.** TF-IDF is the older idea (frequency times rarity). BM25 adds the ceiling on tf and the length normalization, and works better in practice.
- **Inverted index.** Real keyword engines do not scan every document. They keep a map from each word to the list of documents that contain it, so a query only touches matching documents. Our `bm25_scores` rescans everything. That is fine for thousands of chunks.
- **Sparse vs dense.** A keyword vector (one slot per word in the vocabulary, mostly zeros) is called **sparse**. An embedding is **dense**. "Hybrid search" means sparse plus dense. Some models (SPLADE, BGE-M3) learn sparse vectors, too.
- **Weighted RRF.** You can multiply a list's contribution by a weight, if you trust one side more.
- **Score-based fusion.** Normalize with min-max (`(x - min) / (max - min)`) and add with weights. It can beat RRF if you tune it, but it is fragile when scores bunch up.
- **Tokenizer details matter.** Stemming ("deleting" to "delet"), stop-word lists and splitting `snake_case` change what matches. Code and API docs often need a custom tokenizer.
- **Hybrid in databases.** Elasticsearch/OpenSearch, Qdrant, Weaviate and Postgres (full-text search plus pgvector) can do hybrid search inside one system.
- **Reranking is the next step.** After fusion, a stronger model can reorder the top results. That is lesson 23.

## Common mistakes

- Adding raw BM25 and cosine scores.
- Taking only `k` candidates from each side before fusing.
- Counting `df` per occurrence and not per document.
- Not lowercasing, so "Delete" and "delete" do not match.
- Forgetting that a query word that is in no document gives idf but `tf = 0`, so it adds nothing.
- Dividing by zero when all documents are empty (`avg_doc_length = 0`).
- Using `1 / rank` with rank starting at 0. Ranks start at 1.

## Interview corner

**Why hybrid search?**
Vector search catches meaning and synonyms but can miss exact terms (codes, names, numbers). Keyword search is the reverse. Combining them gives better recall on real questions.

**How does BM25 work, in simple words?**
For each query word it multiplies how rare the word is (idf) by how often it appears in the document (with diminishing returns), and adjusts for document length.

**How do you combine two rankings with different score scales?**
Reciprocal Rank Fusion: each item gets the sum of `1 / (k + rank)` over the lists, with `k` about 60. It uses only ranks, so the scales do not matter.

**Why get 20 candidates from each search when you only need 5?**
Fusion needs overlap and choice. An item ranked 8th by one side and 3rd by the other can deserve the top spot.

## Summary

- Vector search finds meaning, keyword search finds exact words. They fail in different places, so use both.
- BM25 = idf (rarity) times flattened tf (frequency), with length normalization. `k1` about 1.5, `b` about 0.75.
- Tokenize: lowercase, split on whitespace, strip punctuation from the ends.
- Do not add scores from different scales. Use RRF: `sum of 1 / (k + rank)`, `k = 60`, ranks start at 1.
- Take more candidates (20) than you need (5), fuse, then cut.
- Project: step 11 adds `copilot/bm25.py` and `copilot/hybrid.py`.
- Reference: `reference/genai-retrieval.md`.
