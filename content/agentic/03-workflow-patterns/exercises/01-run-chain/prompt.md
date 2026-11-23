# A prompt chain

The simplest workflow: a **chain** of model calls. The output of step 1 becomes the input of step 2, and so on. Your code fixes the order.

In the starter you get `ask(client, prompt, system=None, temperature=0)`. It makes one model call and returns the reply text, stripped of spaces at both ends. Use it for **every** model call.

Write `run_chain(client, steps, text)`.

- `steps` is a list of prompt templates (texts). Each contains the marker `{input}`, which stands for the text from the step before.
- Step 1 gets `text`. Step 2 gets the reply of step 1, and so on.
- For each step, make the prompt with `step.replace("{input}", current)`, call `ask`, and keep the reply.
- Return `{"result": the last reply, "outputs": [every reply, in order]}`.
- With no steps, return `{"result": text, "outputs": []}` and make no call.

```python
steps = ["Translate to English: {input}", "Make this one sentence shorter: {input}"]
run_chain(client, steps, "Bonjour tout le monde")
# -> {'result': <reply of step 2>, 'outputs': [<reply of step 1>, <reply of step 2>]}
```

**Think first:** a chain has no loop and no choice. What do you gain by using a chain over one big prompt? (Think about testing each step.)

**Hint:** keep a variable `current`. Start it as `text`, and update it after every call.
