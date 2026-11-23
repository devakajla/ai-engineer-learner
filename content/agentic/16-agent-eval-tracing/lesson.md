---
title: "Agent evaluation and tracing"
summary: See what an agent did with traces and spans, score its answers and its tool path with an eval set, and block bad changes with a regression gate.
plan_ids: []
---

A normal program fails loudly: an exception, a wrong number. An agent fails **quietly**. It gives a fluent answer that is wrong, or reaches the right answer by calling ten tools instead of two, or works today and breaks tomorrow after a prompt change. You cannot see this by reading the final text.

Two tools fix it:

- **Tracing** shows **what happened** in one run (every model call and tool call).
- **Evaluation** measures **how good** the agent is over many test cases, and tells you if a change made it better or worse.

## Tracing: traces and spans

A **trace** is the record of one request, start to end. It holds **spans**. A span is one step: a model call, a tool call, a retrieval. Each span has a name, a kind, how long it took, and extras (tokens used, an error).

```python
trace = [
  {"name": "llm",    "kind": "llm",  "ms": 420, "tokens": 310},
  {"name": "search", "kind": "tool", "ms": 95},
  {"name": "llm",    "kind": "llm",  "ms": 380, "tokens": 540},
]
```

From this you can answer real questions: Why was this request slow? (the second model call.) How many tokens did it cost? (850.) Which tool failed? (look for `error`.)

You build the idea in plain Python (exercise 1). A small wrapper times any function and records a span, even when the function raises:

```python
def traced_call(trace, name, kind, clock, fn, *args, **kwargs):
    start = clock()
    try:
        result = fn(*args, **kwargs)
    except Exception as error:
        add_span(trace, name, kind, start, clock(), error=str(error))
        raise
    add_span(trace, name, kind, start, clock())
    return result
```

What just happened:

1. Note the start time. Run the function.
2. If it fails, still write a span with the error, then **raise again**, so the caller still sees the failure. A trace that hides errors is useless.
3. If it works, write the span and return the result.
4. The `clock` is passed in. In tests you give a fake clock, so the times are exact.

### Step by step: spans (exercise 1)

1. `add_span`: make the dict (duration in milliseconds), append it, return it.
2. `trace_summary`: count spans by kind, add up tokens and times, count errors.
3. `traced_call`: wrap a function with start and end times, with the error path.

## Real tracing tools

In real projects you use a tool that stores traces and shows them as a tree in a web page:

- **Langfuse** (open source, can self-host), **LangSmith** (from the LangChain team), **Arize Phoenix**, and others. Many follow **OpenTelemetry** ideas (traces, spans, attributes).
- Most work by a small **callback or decorator** that you add once. LangChain and LangGraph have built-in support through callbacks (check the docs of your tool for the setup; names and keys change).
- Set secrets such as keys in environment variables, never in code.

What to put on a span: the prompt (or a **hash** of it if it holds private data), the model name, input and output tokens, cost, latency, the tool name and arguments, the user or session id, and the **version** of your prompt and code. Redact personal data.

## Evaluation: three levels

1. **Final answer:** is the answer right? Check for required facts (`must_contain`), compare with a reference answer, or use an LLM judge (GenAI lesson 41).
2. **Trajectory:** did the agent use the right tools in a sensible order? (exercise 2)
3. **Efficiency:** how many steps, tokens, milliseconds and how much money?

Why check the trajectory? An agent can guess a right answer. Or it can answer from memory when it should have used the search tool, and be wrong next week. Checking the path catches this.

```python
trajectory_match(["search", "log", "calc"], ["search", "calc"], "in_order")
# -> True       (the expected tools appear in order; extra steps are allowed)
```

Three modes:

| Mode | Meaning | Use when |
|---|---|---|
| `exact` | the same list | the path is fixed |
| `in_order` | expected tools appear in order, extras allowed | the usual choice |
| `any_order` | expected tools all appear | the order does not matter |

`step_efficiency` gives `expected steps / actual steps`, capped at 1. A value of 0.33 means the agent took three times too many steps.

### Step by step: trajectory check (exercise 2)

1. Get the tool names from the trace (only `tool` spans).
2. For `in_order`, walk through `actual` once with an iterator. Each expected name must be found **after** the previous one.
3. For `any_order`, check that each name is in the list.

## The eval runner

An **eval set** is a list of test cases: an input, what the answer must contain, and the tools you expect. A **runner** runs the agent on each case and scores it (exercise 3):

```python
cases = [{"id": "refund", "input": "How long is a refund?",
          "must_contain": ["5 days"], "expected_tools": ["search_docs"]}]
results = run_eval(agent, cases)
# -> [{'id': 'refund', 'answer_ok': True, 'trajectory_ok': True, 'passed': True,
#      'steps': 1, 'tokens': 100, 'ms': 150}]
```

Good habits for the eval set:

- Start with **20 to 50 real cases**, taken from real user questions and from past failures.
- Include **easy, hard and "should refuse" cases** (questions the docs cannot answer).
- Keep it **fixed** and versioned, so scores are comparable over time.
- One crashing case must not stop the run: record it as a failure.
- Run each case a few times when the model is random, or use temperature 0.

## The regression gate

You change a prompt. Ten cases get better, two get worse. Without a gate you only notice when users complain. A **regression gate** compares a new run with a **baseline** and blocks the change if:

- the pass rate fell by more than a small allowed amount,
- **any** case that passed before now fails (a **regression**),
- cost (tokens) grew a lot.

```python
gate(baseline, new)
# -> {'ok': False, 'reasons': ['pass rate fell by 0.5', 'regressions: a, b']}
```

Run it in CI before every release (exercise 4). Save each run's results, so you can draw the score over time.

## Online evaluation

Offline evals use fixed cases. **Online** evaluation watches real traffic:

- **Feedback:** thumbs up and down, copied answers, retries.
- **Sampling:** a judge model scores 1 to 5% of real traces. People review the worst ones.
- **Alerts:** error rate, p95 latency, cost per request, "I don't know" rate, loop-limit hits.
- **Turn failures into cases.** Every bad real answer becomes a new eval case. This is how the eval set grows.

## Try it live

1. Wrap your agent's model call and tool call with `traced_call` (use `time.perf_counter` as the clock). Run one question and print the trace and `trace_summary`.
2. Write 8 eval cases for your DevDocs agent (or any agent): 5 normal, 2 hard, 1 that the docs cannot answer.
3. Run `run_eval` with the real model. Print `pass_rate` and the failing ids.
4. Change the system prompt a little. Run again. Run `gate` against the first run.
5. (Optional) Sign up for the free tier of a tracing tool and send one trace. Compare it with your own summary.

## A little deeper

- **LLM judge for answers.** For open answers use a judge with a rubric (GenAI lesson 41). Check the judge on cases you scored by hand. Judges are biased (they like long answers and their own style).
- **Flaky evals.** A case that passes 6 times out of 10 is a signal, not noise. Count passes over several runs (`pass@k` is the chance that at least one of k tries works).
- **Datasets of trajectories.** Save good runs and use them as examples or as training data.
- **Tool-level tests.** Test each tool alone (plain unit tests). Most agent bugs are tool bugs.
- **Cost of evals.** Evals call the model many times. Use a small judge, cache, and run the full set only before release.
- **Benchmarks** (SWE-bench, GAIA, tau-bench and others, from memory) compare agents in general. Your own eval set matters more for your product.

## Common mistakes

- Judging an agent by reading a few outputs.
- Only checking the final answer, never the path.
- An eval set that changes every week, so scores cannot be compared.
- Letting one crash stop the whole eval run.
- Averaging away regressions: pass rate stays equal while one important case breaks.
- Logging private data or secrets into traces.
- No version on the trace, so you cannot tell which prompt produced it.
- Never turning real failures into new test cases.

## Interview corner

**How do you evaluate an agent?**
On three levels: the final answer (checks or an LLM judge), the trajectory (right tools, right order) and efficiency (steps, tokens, latency, cost). Use a fixed eval set built from real cases, and run it before each release.

**What is a trace and a span?**
A trace is the record of one request. A span is one step in it (model call, tool call) with timing and attributes such as tokens and errors.

**What would you put in a trace?**
Model, prompt version, input and output tokens, cost, latency, tool name and arguments, errors, session id. Redact personal data and never log secrets.

**What is a regression gate?**
A CI check that compares a new eval run with the baseline and blocks the change if quality fell, any previously passing case now fails, or cost grew too much.

**Offline vs online evaluation?**
Offline: a fixed eval set before release. Online: real traffic with feedback, sampled judging and alerts. Failures found online become new offline cases.

**How do you handle the randomness of LLMs in evals?**
Temperature 0 where possible, several runs per case, count pass rates (not single runs), and look at the variance.

## Summary

- Agents fail quietly, so you need **traces** (what happened) and **evals** (how good it is).
- A trace is a list of **spans**: name, kind, milliseconds, tokens, error. Record a span even when a call fails, and re-raise the error.
- Real tools (Langfuse, LangSmith, Phoenix, OpenTelemetry) store and show traces. Redact private data.
- Evaluate the **answer**, the **trajectory** (`exact`, `in_order`, `any_order`) and the **efficiency**.
- An eval runner scores each case, treats a crash as a failed case, and reports a pass rate.
- A **regression gate** blocks a change on a pass-rate drop, any regression, or big cost growth.
- Online: feedback, sampling, alerts. Turn real failures into new test cases.
- Reference: `reference/agentic-langchain-langgraph.md`.
