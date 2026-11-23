# One worker agent

A **multi-agent** system splits a job between several agents. Each agent is nothing magic: it is a **system prompt plus (maybe) its own tools**. A researcher agent has a "find facts" prompt, a writer agent has a "write clearly" prompt. A **supervisor** decides who works next (exercises 2 to 4).

A worker is described by a dict: `{"description": "finds facts", "system": "You are a researcher."}`. The starter gives you `ask(client, prompt, system=None, temperature=0)`. Write:

1. `run_worker(client, name, worker, task, context="")`: the prompt is `task`. If `context` is not empty, the prompt is `f"{task}\n\nWork so far:\n{context}"`. Call `ask(client, prompt, system=worker["system"])`. Return `{"worker": name, "output": <the reply>}`.
2. `format_results(results)`: `results` is a list of such dicts. Return one line per result, `"<worker>: <output>"`, joined with `"\n"`. An empty list gives `""`.

```python
run_worker(client, "researcher", workers["researcher"], "Explain RAG")
# -> {'worker': 'researcher', 'output': '...'}
format_results([{"worker": "a", "output": "one"}, {"worker": "b", "output": "two"}])
# -> 'a: one\nb: two'
```

**Think first:** why give the writer the researcher's output as "work so far" and not the full chat?

**Hint:** an agent is only a system prompt and a call. Keep each one small and focused.
