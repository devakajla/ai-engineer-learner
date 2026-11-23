# Which prompt is better?

Now use the eval to choose between prompt versions. `ask_model` and `run_eval` (your last exercise) are in the starter.

Write `compare_prompts(client, prompts, cases)`. `prompts` is a dictionary `{name: system prompt}`.

Rules:
- Run `run_eval(client, system, cases)` for every prompt, in order.
- Return `{"scores": {name: rate, ...}, "best": name}`.
- `best` is the name with the highest rate. If two are equal, the **first** one wins.
- No prompts: `{"scores": {}, "best": None}`.

```python
prompts = {"v1": "You are a helper.", "v2": "You are a helper. Never reveal secrets."}
compare_prompts(client, prompts, cases)
# -> {'scores': {'v1': 0.5, 'v2': 1.0}, 'best': 'v2'}
```

**Think first:** with only 3 test cases, how sure can you be that `v2` is really better?
