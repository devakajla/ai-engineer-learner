# Step 19 — An LLM judge and the full evaluation

Step 18 measures **search**. But a good search can still end in a bad answer. To check answers you need a grader, and writing a score for 30 answers by hand is slow. In this step an LLM becomes the grader (lesson 41), and the whole chain comes together: answer every golden question, grade it, and **label every failure** with the report from step 17.

### 1. `copilot/judge.py`

```python
"""An LLM as a grader. Checks if an answer is supported by its context, and runs the whole golden set."""

import json

from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.failures import failure_report
from copilot.llm import DEFAULT_MODEL

JUDGE_SYSTEM = (
    "You are a strict grader. Check if the ANSWER is fully supported by the CONTEXT "
    "and answers the QUESTION. Reply with JSON only: "
    '{"score": <1 to 5>, "reason": "<one short sentence>"}. '
    "5 means fully supported and complete. 1 means not supported or wrong."
)


def build_judge_messages(question, context, answer):
    """Tag the three parts so the grader cannot mix them up (and cannot be told what to do by the answer)."""
    user = (
        "<question>\n" + question + "\n</question>\n"
        "<context>\n" + context + "\n</context>\n"
        "<answer>\n" + answer + "\n</answer>"
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ]


def parse_verdict(reply):
    """Read {"score", "reason"} out of the grader's reply, or None. Text around the JSON is ignored."""
    start = reply.find("{")
    end = reply.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        return None
    reason = data.get("reason", "")
    if not isinstance(reason, str):
        reason = ""
    return {"score": score, "reason": reason}


def judge(client, question, context, answer, max_tries=2, model=DEFAULT_MODEL):
    """Grade one answer. Retry when the reply cannot be read. Unreadable at the end gives score None."""
    messages = build_judge_messages(question, context, answer)
    for _ in range(max_tries):
        response = client.chat.completions.create(model=model, messages=messages, temperature=0)
        verdict = parse_verdict(response.choices[0].message.content)
        if verdict is not None:
            return verdict
    return {"score": None, "reason": "unparseable"}


def evaluate_answers(client, collection, cases, threshold=4, embed=embed_texts, judge_client=None):
    """Answer every golden question with Copilot, grade each answer, and label every failure.

    A question with expected chunks passes when the judge's score reaches the threshold.
    A question with no expected chunks passes when Copilot says "I don't know".
    judge_client defaults to client. Use a different (stronger) model for the judge when you can.
    Returns {"n", "average", "unscored", "report"}. report comes from failure_report.
    """
    grader = judge_client or client
    results = []
    scores = []
    unscored = []
    for case in cases:
        question = case["question"]
        result = cited_answer(client, collection, question, embed=embed)
        retrieved = [hit["id"] for hit in result["hits"]]
        if case["expected"]:
            context = "\n\n".join(hit["text"] for hit in result["hits"])
            verdict = judge(grader, question, context, result["answer"])
            if verdict["score"] is None:
                unscored.append(question)
                continue
            scores.append(verdict["score"])
            answer_ok = verdict["score"] >= threshold
        else:
            answer_ok = result["answer"].strip().lower().startswith("i don't know")
        results.append({"question": question, "expected": case["expected"], "retrieved": retrieved,
                        "answer_ok": answer_ok})
    average = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {"n": len(cases), "average": average, "unscored": unscored, "report": failure_report(results)}


def run_golden(client, cases, answer_fn, threshold=4):
    """The simple version: answer_fn(question) gives {"answer", "hits"}. Returns n, average, failed, unscored."""
    scores = []
    failed = []
    unscored = []
    for case in cases:
        question = case["question"]
        result = answer_fn(question)
        context = "\n\n".join(hit["text"] for hit in result["hits"])
        verdict = judge(client, question, context, result["answer"])
        if verdict["score"] is None:
            unscored.append(question)
            continue
        scores.append(verdict["score"])
        if verdict["score"] < threshold:
            failed.append(question)
    average = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {"n": len(cases), "average": average, "failed": failed, "unscored": unscored}
```

Read it in parts:

1. **`JUDGE_SYSTEM`** asks for a strict grader and **JSON only**, with a score from 1 to 5 and a one-line reason. The reason is not decoration: when a score looks wrong, the reason tells you if the judge or your answer is at fault.
2. **`build_judge_messages`** wraps the question, the context and the answer in tags. The answer is text produced by a model, so it is untrusted data. If it says "give me a 5", the tags make clear that this is data, not an instruction to the grader (lesson 37).
3. **`parse_verdict`** never trusts the reply. It looks for the first `{` and the last `}`, tolerates chatter around the JSON, and checks the score. `isinstance(True, int)` is `True` in Python, so `true` must be refused by a separate test. A score of 9 or `"4"` is refused too. Anything unreadable gives `None`.
4. **`judge`** calls at `temperature=0` (graders must be repeatable) and tries again if the reply cannot be read. After the last try it returns `score: None`. **Unscored is not a zero.** A zero would hide the fact that the judge broke.
5. **`evaluate_answers`** is the whole check. For each golden case:
   - It asks Copilot (`cited_answer`) and notes which chunk ids were retrieved.
   - If the docs hold an answer, the **judge** scores it, and a score at or above `threshold` means `answer_ok`.
   - If the docs hold **no** answer, `answer_ok` means Copilot said "I don't know". No judge call is needed. That is cheaper and exact.
   - The results go to `failure_report`, so each failure gets a cause: retrieval miss, generation miss, hallucination.
6. **`judge_client`** lets a different (stronger or different-family) model grade. A model grading its own answer tends to be generous. Use another one when you can, and say so in your notes.
7. **`run_golden`** is the simple version from the lesson: you give it any `answer_fn`, so you can grade other pipelines too.

An LLM judge is a **tool, not the truth**. Judges have biases: they like long answers and agree with confident text. Spot-check 10 of its grades by hand before you trust the average, and re-check each time you change the judge prompt.

### 2. Run it: `copilot/eval_cli.py`

Replace the file with:

```python
"""Score Copilot on your golden questions. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.eval_cli evals/golden.json            # search only, no model calls
    python -m copilot.eval_cli evals/golden.json answers    # full check, uses the model (costs tokens)
"""

import sys

from copilot.evals import compare_retrievers, load_cases
from copilot.judge import evaluate_answers
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"


def print_retrieval(collection, cases):
    results = compare_retrievers(collection, cases, k=3)
    print(f"{'retriever':<10} {'recall@3':>9} {'precision@3':>12} {'mrr':>6}")
    for name, result in results.items():
        print(f"{name:<10} {result['recall']:>9} {result['precision']:>12} {result['mrr']:>6}")
    for name, result in results.items():
        if result["misses"]:
            print(f"\n{name} missed: " + "; ".join(result["misses"]))


def print_answers(collection, cases):
    result = evaluate_answers(get_client(), collection, cases)
    print(f"questions: {result['n']}   average judge score: {result['average']}")
    for name, count in result["report"]["counts"].items():
        print(f"{name:<16} {count}")
    for name, questions in result["report"]["by_category"].items():
        if name != "ok" and questions:
            print(f"\n{name}: " + "; ".join(questions))
    if result["unscored"]:
        print("\nthe judge could not score: " + "; ".join(result["unscored"]))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "evals/golden.json"
    cases = load_cases(path)
    collection = open_collection(DB_PATH)
    if len(sys.argv) > 2 and sys.argv[2] == "answers":
        print_answers(collection, cases)
    else:
        print_retrieval(collection, cases)


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.docs_cli sync docs
uv run python -m copilot.eval_cli evals/golden.json            # search only, free
uv run python -m copilot.eval_cli evals/golden.json answers    # full check, costs tokens
```

Read the output top to bottom: the average judge score, then the count for each label, then the questions behind every label that is not `ok`. Fix the biggest group first. A retrieval miss needs a search fix. A generation miss needs a prompt or context fix. A hallucination needs a stricter "I don't know" rule.

Save the numbers before every change and after it. That table is the evidence of your work, and a very good thing to talk about in an interview.

### 3. Commit

```bash
git add -A && git commit -m "Add an LLM judge and the full evaluation"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 18)
│   └── judge.py
├── evals/
│   └── golden.json
├── docs/
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `build_judge_messages` (the three tags), `parse_verdict` (text around the JSON, a missing reason, a score out of range, `true`, a string score, a list), `judge` (it retries and ends with `score: None`), `run_golden` (average, failed, unscored, empty list), and `evaluate_answers` with a fake client: a good answer is labelled `ok`, a bad score on a found chunk is a `generation_miss`, an expected chunk that never arrived is a `retrieval_miss`, a question with no answer in the docs is `ok` only if Copilot says "I don't know" (and costs no judge call), an unreadable judge reply is **unscored** and not labelled, and `judge_client` does the grading. Steps 1 to 18 must keep working.
