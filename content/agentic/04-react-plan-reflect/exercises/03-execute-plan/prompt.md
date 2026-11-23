# Run a plan, with a limit

Now run the plan. For each step, build the messages, call the model, and keep the reply as the result of that step. A plan written by a model can be very long, so there is a **hard limit**: run at most `max_steps` steps and report how many were skipped.

In the starter you get `build_step_messages` from the last exercise. Write `execute_plan(client, goal, steps, max_steps=8)`.

- Run the steps in order, but only the first `max_steps` of them.
- For step `i`, the messages are `build_step_messages(goal, steps, results, i)` where `steps` is the **whole** plan (not only the part you run) and `results` holds the replies so far.
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=..., temperature=0)`. The result of the step is `response.choices[0].message.content.strip()`.
- Return `{"results": [...], "steps_run": how many ran, "skipped": how many were left out}`.

```python
execute_plan(client, "Boil an egg", ["Fill a pot", "Boil it", "Peel it"], max_steps=2)
# -> {'results': [<reply 1>, <reply 2>], 'steps_run': 2, 'skipped': 1}
execute_plan(client, "Anything", [])
# -> {'results': [], 'steps_run': 0, 'skipped': 0}
```

**Think first:** what can go wrong if a plan has 40 steps and you run all of them? Who pays?

**Hint:** `steps[:max_steps]` is the part to run. `range(len(...))` gives the indexes.
