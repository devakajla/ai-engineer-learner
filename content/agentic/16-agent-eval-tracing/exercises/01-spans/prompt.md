# Record what the agent did (spans)

You cannot fix what you cannot see. A **trace** is the record of one request. It is a list of **spans**: one per step (a model call, a tool call), each with a name, a kind, how long it took, and extras (tokens, an error). Tools such as Langfuse, LangSmith and OpenTelemetry store and show traces. Here you build the idea in plain Python.

Write (the clock is a function that returns the time in seconds, so tests can fake it):

1. `add_span(trace, name, kind, start, end, **attrs)`: build `{"name": name, "kind": kind, "ms": round((end - start) * 1000), **attrs}`, append it to the list `trace`, and return it.
2. `trace_summary(trace)`: return a dict with `spans` (count), `total_ms` (sum of `ms`), `llm_calls` (spans of kind `"llm"`), `tool_calls` (kind `"tool"`), `tokens` (sum of the `tokens` attribute, missing means 0) and `errors` (spans that have a non-empty `error`).
3. `traced_call(trace, name, kind, clock, fn, *args, **kwargs)`: `start = clock()`, call `fn(*args, **kwargs)`, then add a span with `end = clock()` and return the result. If `fn` raises, add the span with `error=str(error)` and **raise the same error again**.

```python
trace = []
traced_call(trace, "add", "tool", clock, lambda a, b: a + b, 2, b=3)    # -> 5
trace
# -> [{'name': 'add', 'kind': 'tool', 'ms': 200}]
```

**Think first:** why must a failing call still leave a span behind?

**Hint:** `try / except Exception as error: ...; raise`.
