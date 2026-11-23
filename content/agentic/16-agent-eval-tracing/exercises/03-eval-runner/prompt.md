# An eval runner for agents

An **eval** runs your agent on a fixed list of test cases and scores it. You did this for retrieval and RAG (GenAI lessons 25 and 41). For agents you check two things per case: is the **answer** right, and was the **trajectory** right?

The starter gives you the exercise 1 and 2 functions: `add_span`, `trace_summary`, `tool_names`, `trajectory_match`. An **agent** here is a function `agent(text)` that returns `{"answer": str, "trace": [spans]}`. A **case** is `{"id": ..., "input": ..., "must_contain": [words], "expected_tools": [tool names]}` (`must_contain` and `expected_tools` may be missing: treat them as empty lists).

Write:

1. `run_eval(agent, cases, mode="in_order")`: for each case, call the agent and make a result dict with these keys:
   - `id`: the case id.
   - `answer_ok`: every word of `must_contain` is in the answer (ignore case).
   - `trajectory_ok`: `trajectory_match(tool_names(trace), expected_tools, mode)`.
   - `passed`: both are true.
   - `steps`: the number of tool calls. `tokens` and `ms`: from `trace_summary(trace)` (`tokens` and `total_ms`).
   - If the agent **raises**, the result is `{"id": ..., "answer_ok": False, "trajectory_ok": False, "passed": False, "steps": 0, "tokens": 0, "ms": 0, "error": str(error)}` and the run goes on with the next case.
   Return the list of results, in case order.
2. `pass_rate(results)`: the share of results with `passed` true, rounded to 2 decimals. An empty list gives `0.0`.

```python
run_eval(agent, cases)[0]
# -> {'id': 'refund', 'answer_ok': True, 'trajectory_ok': True, 'passed': True, 'steps': 1, 'tokens': 100, 'ms': 150}
```

**Think first:** why must one crashing case not stop the whole eval?

**Hint:** `all(word.lower() in answer for word in must_contain)` is `True` for an empty list.
