# Build the context for one call

**Context engineering** is the job of choosing what goes into the prompt, because the context window is small, costly and gets worse when it is noisy. Four moves: **write** (save facts outside the prompt), **select** (pick only what matters), **compress** (summarise old text), **isolate** (give each sub-task its own small context). This exercise uses **select** and a size **budget**.

The starter gives you `recall(store, user_id, query, k=3)` (from exercise 1) and `size(messages)` (the total number of characters of all `content` texts). Write `build_context(system, store, user_id, history, question, max_chars)`:

1. `facts = recall(store, user_id, question)`.
2. Start the message list with `{"role": "system", "content": system}`.
3. If there are facts, add a second system message: `"Known facts about the user:\n- " + "\n- ".join(facts)`.
4. The last message is `{"role": "user", "content": question}`.
5. In between goes the `history`. While the **total size** of all the messages is more than `max_chars` and there is still history left, drop the **oldest** history message. The system messages and the question are **never** dropped.
6. Return the full list. Do not change the `history` list you were given.

```python
build_context("Be kind.", store, "u", history, "what does Dev like", 10_000)
# -> [system, facts message, ...history..., question]
```

**Think first:** why drop the oldest messages and keep the newest?

**Hint:** copy the history (`kept = list(history)`), then `kept.pop(0)` in a `while` loop.
