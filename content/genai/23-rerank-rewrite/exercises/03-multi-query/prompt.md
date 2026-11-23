# Several versions of one question

One phrasing can miss a good chunk. **Multi-query** asks the model for other ways to say the same question, and searches with all of them.

Write `multi_query(client, question, n=3)`.

Rules:
- One call: `model="qwen/qwen3.8-27b"`, `temperature=0.7`, `max_completion_tokens=200`, one `user` message with exactly: `f"Write {n} different ways to ask this question, one per line, no numbering:\n{question}"`.
- Split the reply into lines (`splitlines()`). For each line: remove spaces at the ends, then remove leading `-`, `*`, `•` and spaces (`.strip().lstrip("-*• ").strip()`).
- Skip empty lines, and skip lines that equal (ignoring upper/lower case) the original question or a line already kept.
- The result starts with the original `question`, then the new lines in order. At most `n` new lines (so the list has at most `n + 1` items).

```python
# reply: "- How can I remove a task?\n- Steps to delete a task\n\n- how do i delete a task?"
multi_query(client, "How do I delete a task?", n=3)
# -> ['How do I delete a task?', 'How can I remove a task?', 'Steps to delete a task']
```
(The last line is the original question in lower case, so it is skipped.)
