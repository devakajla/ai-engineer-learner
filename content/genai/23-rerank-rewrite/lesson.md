---
title: Reranking and query rewriting
summary: Improve what RAG finds - rerank a wide list with a stronger scorer, rewrite follow-up questions, search with several phrasings, and try HyDE.
plan_ids: []
---

A simple RAG finds the top chunks for the question exactly as the user typed it. That works for easy questions. It fails in three common ways:

1. The **right chunk is in the list, but not at the top.** Vector search is rough.
2. The **question is a poor search text.** "And how do I undo it?" means nothing alone.
3. **One phrasing is not enough.** The docs say "remove", the user says "get rid of".

This lesson gives you one fix for each. They are the most common upgrades to a basic RAG.

## Fix 1: rerank

### Why vector search is rough

Remember lesson 14. Each chunk got its vector **before** any question existed. The vector is a summary of the chunk. A question vector is compared with these summaries. That is fast, but a summary loses detail.

A **reranker** is a second, stronger scorer. It reads the question and one chunk **together**, and answers "how well does this chunk answer this question?" It sees all the words of both, so it is more exact. But it is slow: you must run it once per chunk.

So we use **two stages**:

```
Stage 1: vector search   10,000 chunks -> top 20     (fast, rough)
Stage 2: rerank          20 chunks     -> top 5      (slow, exact)
```

Stage 1 is a wide net. Stage 2 picks the best from the net.

### Kinds of rerankers

- **Cross-encoder**: a small model that takes `(question, chunk)` and gives a score. Open ones exist (for example BGE rerankers), and hosted ones too (Cohere Rerank). Fast enough for 20 to 100 chunks.
- **LLM as reranker**: ask a chat model "score each chunk from 0 to 10". It is slower and costs more, but needs no extra model.
- **Diversity reranking (MMR)**: not about relevance only, but also about not repeating. You met it in the Level 3 drill.

### The code part

Whatever the scorer, the code around it is the same. You are given a function `score_fn(question, text)`, call it on each hit, and sort.

Let's practise the pattern with a different example: sort people by a score that a function gives.

1. For each person, make a **copy** and add the new score. (Do not change the original.)
2. Sort by that score, best first.
3. Keep the first `n`.

```python
def score_of(person):
    return person["points"]

def top_people(points_fn, people, n):
    scored = []
    for person in people:
        copy = dict(person)
        copy["points"] = points_fn(person["name"])
        scored.append(copy)
    scored = sorted(scored, key=score_of, reverse=True)
    return scored[:n]

people = [{"name": "Asha"}, {"name": "Ravi"}, {"name": "Mina"}]
top_people(len, people, 2)
# -> [{'name': 'Asha', 'points': 4}, {'name': 'Ravi', 'points': 4}]
```

Here the scorer is `len` (the length of the name). It is a toy, but notice that `points_fn` is **passed in**, so we can swap in any scorer. The first exercise has the same shape.

## Fix 2: rewrite the question

In a chat the user says:

```
User: How do I delete a task?
Bot:  Use the DELETE endpoint.
User: And how do I undo it?
```

The last message alone is a bad search text. A human knows "it" means "deleting a task". A vector search does not.

**Query rewriting** asks a model to make the question stand alone, using the chat history:

```
"And how do I undo it?"  ->  "How do I undo deleting a task?"
```

Then you search with the rewritten text. Two rules:

- With **no history**, do nothing and do **not** call the model. The question already stands alone.
- Use `temperature=0`. You want the same careful rewrite each time.

Show the user the original question. The rewrite is only for the search.

## Fix 3: multi-query

The docs say "remove a task". The user wrote "get rid of a todo". A single search can miss.

**Multi-query**: ask the model for a few other ways to ask the same thing, search with **all** of them, and merge the results.

```
Original:   How do I delete a task?
Variants:   How can I remove a task?
            Steps to erase a task
```

Merging uses RRF (lesson 18): an id found by several queries goes up. Every chunk is ranked in each list, and RRF adds `1 / (60 + rank)` for each list.

Cleaning the model's reply is a real part of the job. Models add bullets, numbers and blank lines. Let's practise the cleaning with a different example: turn a messy list of lines into clean items.

1. Split the reply into lines.
2. Clean each line: remove spaces, then leading `-`, `*` and spaces.
3. Skip empty lines and repeats (ignoring upper/lower case).

```python
def clean_items(text):
    seen = []
    items = []
    for line in text.splitlines():
        item = line.strip().lstrip("-* ").strip()
        if item and item.lower() not in seen:
            seen.append(item.lower())
            items.append(item)
    return items

clean_items("- apple\n* Apple\n\n  pear ")   # -> ['apple', 'pear']
```

`lstrip("-* ")` removes any of the characters `-`, `*` and space from the **left** end. The third exercise does this for questions.

## Fix 4: HyDE (a smart trick)

**HyDE** means *Hypothetical Document Embeddings*. A question and an answer are written in different styles, so their vectors are not always close. HyDE:

1. Ask the model to **write a short fake answer** (it may be wrong, that is fine).
2. Embed the **fake answer**.
3. Search with that vector.

The fake answer looks like a real page of your docs, so it lands near the real page. It is useful when questions are short or vague. The cost is one more model call per search.

## Other query tricks

- **Decomposition.** Split a hard question into smaller ones: "Compare login and signup" becomes two searches.
- **Step-back.** Ask a broader question first ("How does auth work?"), to find the overview.
- **Filters from the question.** "In the tasks docs..." can become a metadata filter (lesson 17).

Every trick costs a model call. Use the **cheapest** one that fixes your measured problem (lesson 25).

## Try it live

Use your RAG from lessons 21 and 22.

1. Find 5 questions where the right chunk is **not** in the top 3. Rerank the top 20 with an LLM scorer (ask for a number 0 to 10 per chunk). Is the right chunk now in the top 3?
2. Have a 3-turn chat and ask a follow-up with "it". Search with and without `rewrite_question`. Compare the top hit.
3. Generate 3 variants of a question. Print what the model wrote. Search with all and merge. Did a new good chunk appear?
4. Try HyDE once and compare its top hit with the plain search.

## A little deeper

- **Latency budget.** A rerank of 20 chunks with a cross-encoder takes tens of milliseconds. An LLM reranker takes seconds. Decide how much waiting is fine.
- **Reranker input limit.** A cross-encoder reads only so many tokens. Long chunks get cut.
- **Score meaning.** Reranker scores are not on the same scale as vector scores. Do not mix them. Use the reranker order only.
- **When to skip it.** If the right chunk is almost always already at rank 1, a reranker adds cost for nothing. Measure first.
- **Fusion of lists.** RRF works with rank only, so it is safe for lists with different score scales (vector, BM25, multi-query).
- **Rewrite risk.** A bad rewrite can change the meaning. Log both texts so you can see mistakes.
- **Caching.** The same question often comes again. Cache the rewrite and the multi-query output.

## Common mistakes

- Reranking all documents instead of a short list.
- Adding the rerank score to the vector score. They are on different scales.
- Calling the model to rewrite a question when there is no history.
- Showing the user the rewritten question as if they typed it.
- Using a high temperature for rewriting.
- Adding every trick at once, with no measurement of what helps.

## Interview corner

**What is a reranker and why use one?**
A stronger scorer that reads the question and a chunk together. Vector search is fast but rough, so you retrieve a wide list (say 20) and rerank it to keep the best few. It raises precision at the top.

**Bi-encoder or cross-encoder?**
A bi-encoder embeds the question and the chunks separately (fast, used for the first stage, chunk vectors can be stored). A cross-encoder reads the pair together (more exact, slow, used for the second stage).

**How do you handle follow-up questions in a RAG chat?**
Rewrite the question into a standalone one using the history, then search with it. Skip the rewrite when there is no history.

**What is HyDE?**
Generate a hypothetical answer with the model and use its embedding for the search. It brings short questions closer to document-style text.

**How do you decide which of these tricks to add?**
Measure retrieval quality with a test set (recall@k, MRR) before and after each one. Keep only what helps enough for its extra cost and latency.

## Summary

- Retrieve wide, then rerank narrow: a cross-encoder (or an LLM) scores each (question, chunk) pair.
- `rerank(score_fn, ...)`: copy each hit, add a score from the function, sort, cut. Do not mix rerank scores with vector scores.
- Rewrite follow-up questions so they stand alone. No history means no call.
- Multi-query: several phrasings, clean the reply, merge the results with RRF.
- HyDE: embed a hypothetical answer instead of the question.
- Every trick adds a call. Measure before and after.
- Project: step 14 adds `copilot/rewrite.py`: rerank, rewrite and multi-query.
- Reference: `reference/genai-retrieval.md`.
