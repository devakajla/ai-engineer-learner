---
title: Evaluating RAG
summary: Measure retrieval with recall@k, precision@k and MRR, check answers for faithfulness, and build a test set so every change is a measured step.
plan_ids: []
---

You changed the chunk size. Is the system better now? "It feels better" is not an answer. Without numbers you will fix one question and break two others, and never know.

**Evaluation** (eval) means: a fixed set of test questions, a way to score the results, and a number you can compare before and after every change. It is the most important habit of an AI engineer, and a favourite interview topic.

## Two things to measure

A RAG system has two jobs, so you measure both separately:

| Job | Question | Measured by |
| --- | --- | --- |
| **Retrieval** | Did the search find the right chunks? | recall@k, precision@k, MRR |
| **Generation** | Is the answer correct, and based on the chunks? | faithfulness, answer correctness (lesson 41) |

Why separate? Lesson 24: the fix is different. If retrieval is poor, a new prompt will not help.

## The test set (the golden set)

A **test set** is a list of questions where you know the right result. For retrieval, each case is:

```python
{"question": "How do I delete a user?", "expected": ["users.md#2"]}
```

`expected` holds the id of the chunk (or chunks) that contain the answer. Tips:

- Start with **20 to 50** real questions. Take them from real users, not only from your head.
- Include **different kinds**: easy ones, paraphrased ones (different words), ones with exact names or codes, and a few that have **no answer** (`expected: []`).
- Write them **by hand**, or let a model suggest questions from chunks and then **check them yourself**.
- Never tune your system on the test set alone. Keep some questions you do not look at while building (a hold-out).

## Retrieval metrics

Say the search returned `["x", "a", "y"]` (best first) and the right chunk is `"a"`.

### Recall@k

> Of the chunks that **should** be found, what fraction is in the top `k`?

```python
def recall(expected, retrieved, k):
    top = retrieved[:k]
    found = sum(1 for item in expected if item in top)
    return found / len(expected)

recall(["a"], ["x", "a", "y"], 3)   # -> 1.0
recall(["a"], ["x", "a", "y"], 1)   # -> 0.0
```

Recall is the key number: **if the right chunk is not in the top `k`, the model cannot use it.** A good target for the search stage is recall@10 above 0.9 (then a reranker narrows it down, lesson 23).

### Precision@k

> Of the `k` results, what fraction is right?

With `["x", "a", "y"]` and `k=3`, one of three is right: precision 0.33. Low precision means a lot of noise in the prompt (costs tokens, can confuse the model). There is a trade-off: a bigger `k` raises recall and lowers precision.

### MRR (mean reciprocal rank)

> How high is the first right chunk? Score `1 / rank`, then average over all questions.

Rank 1 gives 1.0, rank 2 gives 0.5, rank 3 gives 0.33, not found gives 0. MRR shows if the right chunk is **near the top**, which matters because of "lost in the middle" (lesson 24).

### nDCG, briefly

**nDCG** handles cases where chunks are right to different degrees (very relevant, somewhat relevant), and rewards putting the best first. It is common in search research. For RAG, recall@k and MRR are usually enough to start. You write nDCG in the Level 4 drill.

## Worked example: score a list of results

Let's build the pattern of the fourth exercise with a different example: score a quiz game. Each case has a question and the right answer. A function `guess(question)` returns an answer. Report the average score, and the list of questions with a score of 0.

1. Go through the cases.
2. Compute a score for each (here 1 or 0), and add it to a total.
3. If the score is 0, remember the question.
4. At the end, divide the total by the number of cases. Handle zero cases.

```python
def score_game(guess, cases):
    if not cases:
        return {"n": 0, "average": 0.0, "wrong": []}
    total = 0
    wrong = []
    for case in cases:
        score = 1 if guess(case["question"]) == case["answer"] else 0
        total += score
        if score == 0:
            wrong.append(case["question"])
    return {"n": len(cases), "average": round(total / len(cases), 4), "wrong": wrong}

def guess(question):
    return {"2+2": "4", "3+3": "7"}[question]

cases = [{"question": "2+2", "answer": "4"}, {"question": "3+3", "answer": "6"}]
print(score_game(guess, cases))   # -> {'n': 2, 'average': 0.5, 'wrong': ['3+3']}
```

The `wrong` list is the most useful part: it shows **where to look first**. The same applies to the `misses` list in your retrieval evaluation.

## Generation metrics

Now the answer. Three questions:

1. **Faithfulness (groundedness):** is every claim in the answer supported by the retrieved chunks? An unfaithful answer is a hallucination, even if it happens to be true.
2. **Answer relevance:** does the answer address the question?
3. **Correctness:** does it match the known right answer?

Scoring these needs reading text, so you use either:
- **Cheap checks in code**: does the answer have citations? Do the cited numbers exist (lesson 22)? Does it contain the key fact (a required word or number)? Is "I don't know" used when `expected` is empty?
- **A model as the judge** (lesson 41), for the things code cannot check.

## Offline and online evaluation

- **Offline**: run the test set on your laptop or in CI before each change. Fast and repeatable.
- **Online**: look at real traffic: thumbs up and down, follow-up questions that say "no, that is wrong", retries, fallbacks to a human. Log these (lesson 29 and Level 5).

You need both. Offline stops regressions. Online finds the questions you did not think of. Add each real failure to the test set, so it can never come back unnoticed.

## Tools

Libraries exist for this (for example **Ragas**, **TruLens**, **DeepEval**, and tracing tools like **Langfuse** and **LangSmith**). They give ready metrics and dashboards. They change quickly, so check their docs. The ideas above are what you must understand. The numbers are only as good as the test set.

## Try it live

1. Write 15 test cases for your RAG on your own docs. Use at least 3 with different wording than the docs, 2 with exact names, and 3 with no answer.
2. Run `evaluate_retrieval` with `k=3` and `k=8`. Write down recall, precision and MRR for both.
3. Look at the `misses`. For each, find why (lesson 24).
4. Make **one** change (chunk size, or hybrid search instead of vector only). Run again. Did the numbers move? Did a question that worked before now fail?

## A little deeper

- **Small test sets are noisy.** With 20 questions, one question changes recall by 5 points. Do not trust small differences. Grow the set over time.
- **Label problems.** Sometimes two chunks both answer. List all of them in `expected`, or your recall will look too low.
- **Synthetic test sets.** A model can write questions from chunks. They are often too easy and use the chunk's own words. Mix them with real questions.
- **Metric vs goal.** A high recall does not guarantee good answers. And the reverse: good answers on easy questions hide retrieval gaps. Look at both.
- **Retrieval-only evals are cheap**: no model call, run in seconds. Run them on every change. The answer evals cost money, run them less often.
- **Regression tests.** The test set is also a regression test: a change that drops a number must be explained.
- **Latency and cost** are part of quality too. Track tokens per answer and the time per stage.

## Common mistakes

- No test set, only "it feels better".
- Test questions copied from the docs, using the same words (too easy).
- No questions without an answer, so "I don't know" is never tested.
- Measuring only the final answer, so you cannot tell retrieval from generation problems.
- Tuning on the test set until it is perfect (overfitting), then failing on real users.
- Comparing numbers from different test sets.
- Ignoring the `misses` list.

## Interview corner

**How do you evaluate a RAG system?**
Separate retrieval and generation. For retrieval: a test set with the expected chunks, and metrics like recall@k, precision@k and MRR. For generation: faithfulness (is the answer supported by the chunks), relevance and correctness, with code checks and an LLM judge. Run offline on every change, and learn from online feedback.

**What is recall@k, and why does it matter most?**
The share of the chunks that should be found that are in the top `k`. If the right chunk is not retrieved, the model cannot use it, so it limits everything after.

**What is MRR?**
Mean reciprocal rank: the average of `1 / rank` of the first right result. It rewards putting the right chunk near the top.

**What is faithfulness?**
Whether every claim in the answer is supported by the retrieved context. An unfaithful answer is a hallucination.

**How do you build a test set?**
Collect real questions, write the expected chunks by hand, include paraphrases, exact-term questions and unanswerable questions, keep a hold-out part, and add every real failure over time.

## Summary

- Evaluate retrieval and generation separately.
- A test set (golden set) of 20 to 50 real questions with expected chunk ids, including questions with no answer.
- Recall@k: share of expected chunks in the top `k`. Precision@k: share of the `k` results that are right. MRR: average of `1 / rank` of the first right chunk.
- Raising `k` raises recall and lowers precision.
- Faithfulness: every claim is supported by the chunks. Check with code where you can, and with a judge model (lesson 41).
- Run offline before each change. Learn from online feedback. Add each failure to the test set.
- Small test sets are noisy. Do not tune on the whole set.
- Project: step 18 adds `copilot/evals.py`: a golden set and retrieval metrics.
- Reference: `reference/genai-retrieval.md`.
