# Decide: answer, rewrite or give up

After grading, the graph needs a **decision**. Keep it in a small plain function so you can test it without any graph. The three outcomes:

- there are relevant docs: **answer**.
- no relevant docs, but you may still try again: **rewrite** the question and search again.
- no relevant docs and no tries left: **give up** honestly. Do not make up an answer.

The starter gives you `ask(...)` again. Write:

1. `decide_next(state)`: `state` is a dict with `relevant` (list), `tries` (searches done so far) and `max_tries`. Return `"answer"` if `relevant` is not empty. Else return `"give_up"` if `tries >= max_tries`. Else return `"rewrite"`.
2. `rewrite_question(client, question)`: one model call with exactly this prompt, and return the stripped reply:
   `"Rewrite this question so a search engine finds better results. Reply with the new question only.\n\n" + question`

```python
decide_next({"relevant": [], "tries": 1, "max_tries": 2})   # -> 'rewrite'
decide_next({"relevant": [], "tries": 2, "max_tries": 2})   # -> 'give_up'
```

**Think first:** without a `max_tries` check, what could this loop do on a question the documents cannot answer?

**Hint:** check `relevant` first, then the tries, then fall through to `"rewrite"`.
