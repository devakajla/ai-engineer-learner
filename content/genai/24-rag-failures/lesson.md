---
title: RAG failure modes
summary: Learn the ways a RAG system goes wrong (retrieval, context and generation), how to tell which one it is, and the standard fix for each.
plan_ids: []
---

Your RAG demo works on five questions. Then real users arrive and some answers are wrong. What now?

The worst response is to **change the prompt and hope**. A RAG system has many parts, and the fix depends on **which part failed**. This lesson gives you a map of the failures and a habit: **find the failing stage first**.

## The pipeline, with places to fail

```
question -> [1 rewrite] -> [2 search] -> [3 pick + order chunks] -> [4 prompt] -> [5 model] -> answer
                 |             |                  |                                  |
              bad query    wrong chunks      noise, repeats,                  ignores context,
                                             lost in the middle                invents, wrong merge
```

There are three families:

1. **Retrieval failures**: the right chunk was not found.
2. **Context failures**: the right chunk was found, but the model got a bad package.
3. **Generation failures**: the model had what it needed and still answered badly.

## The first habit: look at the chunks

When an answer is wrong, **print the retrieved chunks** before anything else. Then ask:

- Is the right chunk in the list? If **no**: retrieval failure.
- If **yes**: did the answer use it correctly? If **no**: generation failure.

This one check splits the problem in two and saves you days. In the first exercise you turn it into code:

| Expected chunk found? | Answer good? | Class |
| --- | --- | --- |
| no | any | retrieval miss |
| yes | no | generation miss |
| yes | yes | ok |
| (no answer exists) | model said "I don't know" | ok |
| (no answer exists) | model made something up | hallucination |

Counting the classes over a whole test set tells you where to spend your time. If 70% of failures are retrieval misses, a better prompt will not help.

Let's practise the **count by category** pattern with a different example: sort test results into "pass", "slow" and "error".

1. Make a dictionary with every category, each starting at 0, so no key is missing.
2. For each result, decide its category and add 1.

```python
def classify(result):
    if result["error"]:
        return "error"
    if result["ms"] > 1000:
        return "slow"
    return "pass"

def summarize(results):
    counts = {"pass": 0, "slow": 0, "error": 0}
    for result in results:
        counts[classify(result)] += 1
    return counts

summarize([{"error": False, "ms": 200}, {"error": False, "ms": 2000}, {"error": True, "ms": 5}])
# -> {'pass': 1, 'slow': 1, 'error': 1}
```

Starting with all keys at 0 means the report always has the same shape. The second exercise builds the same kind of report.

## Retrieval failures

| Cause | Sign | Fix |
| --- | --- | --- |
| **The answer is not in the index** | No chunk has it | Add the document (ingestion, lesson 39) |
| **Vocabulary mismatch** | The user says "get rid of", the docs say "delete" | Hybrid search (18), multi-query, HyDE (23) |
| **Exact terms missed** | Error codes and names are not found | BM25 in hybrid search (18) |
| **Bad chunks** | The answer is cut in half, or the chunk is too big and vague | Better chunking, overlap, parent retrieval (16) |
| **Vague or follow-up question** | "And the second one?" | Query rewriting (23) |
| **`k` too small** | The right chunk is rank 8 and you take 5 | Retrieve more, then rerank (23) |
| **Filter too strict** | Metadata or access filters drop the right chunk | Check filters (lesson 40) |
| **Wrong embedding setup** | Different models for docs and queries, missing prefix | Fix the config (14) |
| **Stale index** | The doc changed but the chunks did not | Incremental update (39) |

### Bad chunks, a closer look

Chunking causes more trouble than most people expect:

- **Too small**: a chunk like "Yes, it can." has no subject. It matches nothing and explains nothing.
- **Too big**: one vector must summarize many topics, so it is vague, and the prompt fills with noise.
- **Cut in the wrong place**: a rule in one chunk and its exception in the next.
- **No context**: a chunk `"The limit is 100."` does not say *which* limit. Adding the title and heading to the chunk text (contextual chunks, lesson 42) helps.

## Context failures

The right chunk is in the list, but the package given to the model is poor.

- **Lost in the middle.** Models use the start and the end of a long context better than the middle. If the key chunk sits in the middle of 10 chunks, it may be ignored. Fixes: fewer chunks, and put the best at the two ends.
- **Repeats.** The same text three times pushes out other chunks.
- **One source dominates.** Ten chunks from the same page and nothing from the others.
- **Contradictions.** An old and a new version of a rule both appear. The model picks one. Fix with freshness rules (lesson 40), and tell the model to prefer the newest.
- **Too much noise.** A lot of weakly related chunks. Use a minimum score and a reranker (23).

Let's practise the **reorder for the ends** with a different example: seat the best guests at the two ends of a table. Guests come ranked, best first.

1. Take the guests at positions 0, 2, 4, ... for the front.
2. Take the guests at positions 1, 3, 5, ... for the back, and reverse them.
3. Seat the front, then the back.

```python
def seat(guests):
    front = guests[0::2]
    back = guests[1::2]
    back.reverse()
    return front + back

seat(["A", "B", "C", "D", "E"])   # -> ['A', 'C', 'E', 'D', 'B']
```

`guests[0::2]` means "start at 0, take every second item". `guests[1::2]` starts at 1. `A` is first, `B` is last, and the weakest guest `E` sits near the middle. The fourth exercise does this for chunks.

## Generation failures

The model has the right chunk and still gets it wrong.

| Cause | Sign | Fix |
| --- | --- | --- |
| **Ignores the context** | Answers from its own memory | Stronger "only the context" rule, citations (22), lower temperature |
| **Over-trusts its memory** | Mixes old knowledge with the chunk | Tell it the context is the truth, even if it differs |
| **Merges two chunks wrongly** | Combines facts that do not go together | Smaller `k`, clearer chunks, ask it to quote |
| **Over-refuses** | Says "I don't know" although the answer is there | Lower the minimum score, soften the rule, check the prompt |
| **Invents citations** | Cites `[7]` | Check citations (22) |
| **Format errors** | Breaks the JSON or the style | Validate and repair (10) |
| **Multi-step questions** | "Compare A and B" needs two searches | Query decomposition, agentic RAG (lesson 42) |

## Failures outside the three families

- **Prompt injection** in a chunk (lesson 37).
- **Permission leaks** (lesson 40).
- **Latency and cost**: too many chunks, too many calls (lesson 29 and Level 5).
- **No answer exists**: the bot must say "I don't know" (lesson 21).

## How to work: a loop

1. Collect real failing questions. Keep them in a test file.
2. For each, find the stage that failed (print the chunks).
3. Fix **one thing**, in that stage.
4. Run **all** the test questions again (lesson 25). Did anything else break?
5. Repeat.

## Try it live

1. Take your RAG from the earlier lessons. Write 10 questions. For each, note the id of the chunk that should answer it. (Three of them should have **no** answer in your docs.)
2. Run them. For each, print the retrieved ids and the answer. Use your `classify_failure`, and build a report.
3. Look at the biggest failure group. Choose one fix from the tables above. Apply it. Run again. Did the counts improve?
4. Try "lost in the middle": put the right chunk in the middle of 8 chunks and ask. Then reorder, and ask again.

## A little deeper

- **Position bias** is measured in research ("lost in the middle"). Newer long-context models are better, but not immune.
- **Chunk size experiments.** Try three sizes (for example 200, 500, 1000 characters) and compare recall@k (lesson 25). The best size depends on your documents.
- **Parent-child retrieval.** Search small chunks (precise), but send the bigger parent section (complete). It fixes many "cut in half" problems (lesson 42).
- **Answerability.** Some questions need information that is spread across many documents. Plain RAG is weak on "summarize everything about X" and on counting. Those need other designs.
- **Evaluation first.** Without a test set you cannot know if a change helped. It is the topic of the next lessons.
- **Silent failures.** The worst failure is a confident wrong answer with a plausible citation. Logging the retrieved chunks makes it findable.

## Common mistakes

- Changing the prompt before looking at the retrieved chunks.
- Testing only on questions that you know work.
- Fixing five things at once.
- No questions without an answer in the test set, so "I don't know" is never tested.
- Sending 15 chunks "to be safe".
- Cutting chunks by character count only, and never reading them.

## Interview corner

**A RAG answer is wrong. How do you debug it?**
First check if the right chunk was retrieved. If not, it is a retrieval problem (chunking, query, embedding, filters, missing data). If it was, check the context package (order, noise, repeats), and then generation (prompt, model, temperature). Fix one stage and re-run the test set.

**What is the "lost in the middle" problem?**
Models use information at the start and the end of the context better than information in the middle. Reduce the number of chunks, rerank, and put the best chunks at the ends.

**Why can chunking hurt RAG quality?**
Chunks that are too small have no context. Chunks that are too big are vague and noisy. Cuts in the wrong place split an answer. Fix with a suitable size, overlap, structure-aware splitting, titles in the chunk text and parent-child retrieval.

**How do you handle questions that have no answer in the documents?**
A minimum score, a rule that allows "I don't know", and test questions that have no answer, to check that the system refuses instead of inventing.

## Summary

- Three families of failure: retrieval (not found), context (bad package), generation (bad answer).
- First habit: print the retrieved chunks. Right chunk missing means retrieval. Present but wrong answer means generation.
- Count failure classes over a test set to choose what to fix.
- Retrieval fixes: hybrid search, multi-query, rewrite, better chunks, larger `k` plus rerank, correct filters, fresh index.
- Context fixes: fewer chunks, remove repeats, limit chunks per source, put the best at the ends.
- Generation fixes: strict context rule, citations, low temperature, validation.
- Work in a loop: collect failures, find the stage, fix one thing, re-run everything.
- Project: step 17 adds `copilot/context.py` and `copilot/failures.py`: clean context and failure labels.
- Reference: `reference/genai-retrieval.md`.
