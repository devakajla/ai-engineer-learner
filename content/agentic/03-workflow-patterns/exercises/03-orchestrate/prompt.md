# Orchestrator and workers

For a task that is too big for one call, an **orchestrator** asks the model to split it into subtasks, **workers** (one call each) do the subtasks, and a last call **combines** the results. Unlike a fixed chain, the **number** of subtasks is decided by the model.

In the starter you get `ask(client, prompt, system=None, temperature=0)`. It makes one model call and returns the reply text, stripped of spaces at both ends. Use it for **every** model call.

Write `orchestrate(client, task, max_subtasks=3)`.

1. **Plan call.** `ask(client, f"Split this task into at most {max_subtasks} short subtasks, one per line, no numbering:\n{task}")`.
2. **Clean the plan.** Split the reply into lines. For each line remove spaces at both ends and leading bullet characters (`-`, `*`, `•`) and spaces after them. Skip empty lines. Keep only the first `max_subtasks` lines. (The tests use plain lines and `- ` bullets.)
3. **No subtasks?** Return `{"subtasks": [], "results": [], "answer": ask(client, task)}`: just answer the task directly.
4. **Worker calls**, one per subtask, in order: `ask(client, f"Task: {task}\nSubtask: {subtask}\nDo only this subtask.")`.
5. **Combine call.** Number the results from 1 as `"1. ..."`, one per line, and call `ask(client, f"Combine these results into one answer for the task.\n\nTask: {task}\n\nResults:\n{numbered}")`.
6. Return `{"subtasks": [...], "results": [...], "answer": the combined reply}`.

```python
orchestrate(client, "Write a short guide to making tea")
# plan reply:  "- boil water\n- steep the leaves\n- add milk"
# -> {'subtasks': ['boil water', 'steep the leaves', 'add milk'], 'results': [..3 replies..], 'answer': <combined>}
```

**Think first:** workers do not see each other's results. When is that a problem, and when is it a benefit?

**Hint:** `text.splitlines()` gives the lines. `line.strip().lstrip("-*• ")` removes bullets. `enumerate(results, start=1)` gives numbers from 1.
