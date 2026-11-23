# Route a question to the right handler

A **router** looks at the input, picks a path, and sends it there. Each path has its own prompt, tuned for one kind of question. This is cheaper and better than one giant prompt for everything.

In the starter you get `ask(client, prompt, system=None, temperature=0)`. It makes one model call and returns the reply text, stripped of spaces at both ends. Use it for **every** model call.

Write `route(client, question, routes)`.

- `routes` is a dictionary `{label: system prompt}`. It always has the label `"other"`.
- **Call 1, the classifier:** call `ask` with a prompt that lists all the labels (joined with `", "`, in the order of the dictionary), tells the model to answer with only the label, and ends with the question. The reply is the label guess.
- Clean the guess: make it lowercase and remove a final `"."` with `.strip(".")`. If the cleaned text is **not** a key of `routes`, use `"other"`. Never trust the model's format.
- **Call 2, the handler:** call `ask(client, question, system=routes[label])`.
- Return `{"label": label, "answer": the handler reply}`.

```python
routes = {
    "billing": "You are a billing expert. Be short.",
    "tech": "You are a support engineer. Give steps.",
    "other": "You are a friendly assistant.",
}
route(client, "My card was charged twice", routes)
# -> {'label': 'billing', 'answer': <reply of the billing handler>}
```

**Think first:** why is a classifier call at temperature 0 better than asking the model to answer and to guess the type in the same call?

**Hint:** the classifier prompt can be any wording, but it must contain every label and the question. The tests check that.
