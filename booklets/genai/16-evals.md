# 16. Evaluation: how you know it works

In normal software, tests say pass or fail. With LLMs the output changes every time, so "it looked fine on two examples" is how most teams fool themselves. **Evaluation** (evals) means measuring quality on a **fixed set of examples**, so every change can be compared with the last. It is the most important professional habit in this booklet.

## The golden dataset

A **golden dataset** is a list of test cases you trust. For RAG each case holds:

```python
case = {
    "question": "How long do I have to ask for a refund?",
    "relevant_ids": ["refund#1"],        # which chunks should be found
    "reference": "30 days",             # a short correct answer
}
```

How to build it: start with **20 to 50** real questions (from users, tickets, or your own reading of the docs). Include easy ones, hard ones, and some that have **no answer** in the documents. Write the reference answers carefully. Add new failures as new cases forever. A small, honest set beats a large, sloppy one.

## Evaluate retrieval first

Retrieval can be tested with **no model call**, so it is cheap and exact. Use the metrics of chapter 13:

- **recall@k:** did the relevant chunk appear in the top k?
- **precision@k:** how much of the top k was relevant?
- **MRR:** how high was the first relevant result?

```python
def recall_at_k(retrieved, relevant, k):
    hits = [d for d in retrieved[:k] if d in relevant]
    return len(hits) / len(relevant)

def mrr(results):
    total = 0.0
    for retrieved, relevant in results:
        for rank, doc in enumerate(retrieved, start=1):
            if doc in relevant:
                total += 1 / rank
                break
    return total / len(results)

results = [(["a", "x", "c"], {"a"}), (["x", "b", "y"], {"b"}), (["x", "y", "z"], {"q"})]
print(round(mrr(results), 2))
# -> 0.5
print(recall_at_k(["a", "x", "c"], {"a", "c"}, 2))
# -> 0.5
```

(We checked these by hand: the three cases give reciprocal ranks 1, 1/2 and 0, average 0.5. The second line: only `a` is in the top 2 and two are relevant, so 0.5.)

If recall@k is low, **no prompt can fix it**. The answer was never in front of the model. Fix retrieval first.

## Evaluate generation

Now check the answer. Common measures:

| Measure | Question it asks |
| --- | --- |
| **Faithfulness / groundedness** | is every claim supported by the retrieved chunks? |
| **Answer relevance** | does the answer address the question? |
| **Correctness** | does it match the reference answer? |
| **Refusal accuracy** | does it say "I do not know" when it should, and only then? |

Cheap checks come first: does it contain the key fact (`"30" in answer`), the citation, valid JSON? Write plain asserts for what is exact.

## LLM-as-judge

For fuzzy quality, use **another model to grade**. Give it the question, the sources and the answer, with a clear rubric, and ask for a score and a short reason in JSON (chapter 7).

```python
JUDGE = (
    "You grade a RAG answer. Sources and answer follow. "
    "Reply with JSON: {\"faithful\": true or false, \"reason\": short text}. "
    "faithful is true only if every claim is supported by the sources."
)
```

Strengths: scales, handles meaning. Weaknesses, which you must know for interviews:

- **Position bias:** prefers the first answer when comparing two.
- **Verbosity bias:** prefers longer answers.
- **Self-preference:** a model tends to like its own style.
- It can simply be **wrong**.

So: use a **clear rubric**, low temperature, structured output, swap the order when comparing, and **check the judge against a few human-labelled cases** (does it agree with you?).

## Tools

**RAGAS**, **DeepEval**, **TruLens**, **promptfoo** and **LangSmith/Langfuse** datasets give ready metrics (faithfulness, answer relevance, context precision and recall) and dashboards. They are all built on the ideas above. Learn the ideas first, and then any tool is easy.

## Regression evals in CI

Treat evals like unit tests. Every pull request that changes a prompt, chunking or model runs the eval set, and **fails if a score drops** below the saved baseline.

@@ flow | Figure 16.1: the eval loop.
Change|prompt, chunk size, model|blue -> Run eval set|retrieval + generation scores|yellow -> Compare|with the last baseline|purple -> Decide|ship, or fix the failures|green
@@ end

```python
def check_no_regression(scores, baseline, tolerance=0.02):
    problems = []
    for name, value in scores.items():
        if value < baseline[name] - tolerance:
            problems.append(f"{name}: {value:.2f} is below baseline {baseline[name]:.2f}")
    return problems

print(check_no_regression({"recall": 0.80, "faithful": 0.95}, {"recall": 0.90, "faithful": 0.94}))
# -> ['recall: 0.80 is below baseline 0.90']
```

`faithful` went up and `recall` dropped by 0.10, more than the 0.02 tolerance, so the check reports it. In CI you would `assert not problems` and fail the build.

Practical tips: keep the eval set under a few minutes of runtime (use a cheap model), record each run with its settings (model, chunk size, prompt version), and read the **failed cases** by hand, not only the average. Averages hide patterns.

## Online feedback

Offline evals miss real users. Add thumbs up and down, "was this helpful?", and log them with the question and the retrieved chunks (chapter 21). Add bad cases to the golden set.

::: {.box .checkpoint}
**Checkpoint:** you can name four RAG metrics, three judge biases, and explain why retrieval is evaluated before generation.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Judging quality by trying two or three questions.
- No questions that should be refused.
- Only measuring the final answer, so retrieval bugs hide.
- Trusting an LLM judge without checking it against human labels.
- Changing three things between two eval runs.
- Reading only the average score, never the failures.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you evaluate a RAG system?** A golden dataset. Retrieval metrics (recall@k, precision@k, MRR) and generation metrics (faithfulness, answer relevance, correctness), plus a check that it refuses unanswerable questions.

**Q: What is faithfulness?** Whether every claim in the answer is supported by the retrieved context.

**Q: What are the weaknesses of LLM-as-judge?** Position bias, verbosity bias, self-preference and plain errors. Mitigate with rubrics, swapped order, and calibration against human labels.

**Q: How do you stop regressions?** Run the eval set in CI and fail when a metric falls below baseline.

**Q: Recall is low. What do you do?** Improve retrieval: parsing, chunking, embedder, hybrid search, K. Prompt changes cannot help if the chunk is never retrieved.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write ten golden cases for your own toy documents, two of them with no answer.
2. Compute recall@3 and MRR for your toy retriever.
3. Write `check_no_regression` as a pytest test that fails when a score drops.
4. Write a judge prompt for "is the answer polite?" with a rubric. Test it with a fake client.
5. Compare chunk sizes 100 and 300 characters on your cases. Which has better recall@3?
6. **Think:** why does a judge that prefers long answers push a system in the wrong direction?
:::
