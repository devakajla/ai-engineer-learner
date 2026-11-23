# Evaluator and optimizer

One call writes a draft. A second call **judges** it. If the judge is not happy, a third call **rewrites** the draft using the feedback. Repeat, but with a hard limit. This is the **evaluator-optimizer** pattern. It is a loop, but your code controls it, so it is still a workflow.

In the starter you get `ask(client, prompt, system=None, temperature=0)`. It makes one model call and returns the reply text, stripped of spaces at both ends. Use it for **every** model call.

Write `improve_loop(client, task, max_rounds=3)`.

1. **Draft:** `draft = ask(client, task)`.
2. **Evaluate** the draft with `ask(client, f"Task: {task}\n\nDraft:\n{draft}\n\nIf the draft is good, reply exactly OK. Otherwise reply with one short sentence of feedback.")`. (`ask` already strips the reply.)
3. If the verdict, after removing a final `"."` with `.rstrip(".")` and making it uppercase, equals `"OK"`: return `{"text": draft, "rounds": revisions so far, "accepted": True}`.
4. If it is not OK and you already made `max_rounds` revisions: return `{"text": draft, "rounds": max_rounds, "accepted": False}`.
5. Otherwise **revise** with `ask(client, f"Task: {task}\n\nDraft:\n{draft}\n\nFeedback: {verdict}\n\nRewrite the draft to fix the feedback. Reply with the new draft only.")`, count one more revision, and go back to step 2 with the new draft.

The new draft is always evaluated again. So the most calls are `1 + (max_rounds + 1) + max_rounds`.

```python
# draft "v1" -> verdict "Too long." -> revision "v2" -> verdict "OK"
improve_loop(client, "Write a slogan")
# -> {'text': 'v2', 'rounds': 1, 'accepted': True}
```

**Think first:** why is a hard limit (`max_rounds`) a must? What can go wrong if the judge is never satisfied?

**Hint:** a `while True:` loop with `return` inside works well. Keep a counter `revisions`.
