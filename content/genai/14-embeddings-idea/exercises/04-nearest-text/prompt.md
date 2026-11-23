# The nearest text

You can now turn text into a vector and measure the distance between two vectors. Put the two together: a tiny **search**.

`toy_embed(text, vocab)` (exercise 1) and `euclidean(a, b)` (exercise 3) are in the starter. Write `nearest_text(query, texts, vocab)`. It returns the text from `texts` that is **closest** to the query.

Rules:
- Turn the query into a vector with `toy_embed(query, vocab)`. Turn each text into a vector the same way.
- Return the text with the **smallest** Euclidean distance to the query vector.
- If two texts have the same distance, return the **earlier** one.
- If `texts` is empty, return `None`.

```python
vocab = ["task", "login", "token"]
texts = ["delete a task", "login with a token", "list every task"]
nearest_text("login token", texts, vocab)   # -> 'login with a token'
nearest_text("task", texts, vocab)          # -> 'delete a task'   (tie with 'list every task': the earlier one wins)
nearest_text("task", [], vocab)             # -> None
```

**Think first:** is a small distance good or bad here?
