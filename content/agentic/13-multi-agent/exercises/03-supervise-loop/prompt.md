# The supervisor loop (plain Python)

Before using a graph, write the loop in plain Python so you see it clearly: ask the supervisor, run the chosen worker, add its result to the work so far, ask again. Stop on `FINISH`, on an unknown name, or after `max_steps`.

The starter gives you `ask`, `run_worker`, `format_results`, `supervisor_prompt` and `parse_choice`. Write `supervise(client, workers, task, max_steps=4)`:

1. `results = []`, `finished = False`.
2. Repeat up to `max_steps` times:
   - `reply = ask(client, supervisor_prompt(task, workers, results))` and `choice = parse_choice(reply, list(workers))`.
   - If `choice == "FINISH"`: set `finished = True` and stop the loop.
   - If `choice is None` (an unknown name): stop the loop (`finished` stays `False`).
   - Otherwise run the worker: `run_worker(client, choice, workers[choice], task, format_results(results))` and add the result dict to `results`.
3. Return `{"results": results, "steps": len(results), "finished": finished}`.

```python
supervise(client, workers, "Explain RAG")
# -> {'results': [{'worker': 'researcher', ...}, {'worker': 'writer', ...}], 'steps': 2, 'finished': True}
```

**Think first:** what two limits stop a supervisor that never says FINISH? (One is `max_steps`. What is the other, and why is it useful?)

**Hint:** use `for _ in range(max_steps):` with `break`. The step cap is your cost cap too.
