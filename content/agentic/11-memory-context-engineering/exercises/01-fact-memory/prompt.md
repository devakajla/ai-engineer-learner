# Long-term memory: save and recall facts

A checkpointer (lesson 9) remembers **one conversation**. **Long-term memory** keeps facts across conversations: "Dev likes Python", "Dev lives in Pune". You save them under a **user id** and later **recall** only the ones that matter to the new question. The simplest store is a dict: `{user_id: [fact, fact, ...]}`. (LangGraph has a `Store` for this. The idea is the same.)

Write:

1. `save_fact(store, user_id, fact)`: add `fact.strip()` to the user's list (create the list if needed). If the same fact is already there (compare in lower case, ignoring spaces at both ends), do **not** add it and return `False`. Otherwise return `True`.
2. `recall(store, user_id, query, k=3)`: score each fact of the user by the **number of query words** (lower case, split on spaces, as a set) that are also in the fact's words. Keep only scores above 0. Return the best `k` facts, highest score first (ties keep the saved order). An unknown user returns `[]`.

```python
store = {}
save_fact(store, "u1", "Dev likes strong tea in the morning")
recall(store, "u1", "strong tea morning")
# -> ['Dev likes strong tea in the morning']
```

**Think first:** why not put **all** the facts into every prompt?

**Hint:** `store.setdefault(user_id, [])` gives the list and creates it when missing.
