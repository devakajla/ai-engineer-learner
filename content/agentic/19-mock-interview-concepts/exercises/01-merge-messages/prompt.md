# Interview drill 1: the `add_messages` reducer

**Asked as:** "In LangGraph, how does the `messages` key of the state get updated? Write a small version of that reducer."

LangGraph's `add_messages` reducer (lesson 8) **appends** new messages to the list, but if a new message has the same `id` as an old one, it **replaces** the old one in place. This is how an edit or a streamed update keeps its position.

Write `merge_messages(old, new)`. Messages are dicts. A message may have an `"id"` key (or not).

- Start from a copy of `old` (do not change `old` or `new`).
- For each message in `new`, in order: if it has an id that is already in the result, replace that entry **at the same position**. Otherwise append it.
- Messages **without** an id are always appended.

```python
merge_messages([{"id": "1", "text": "a"}], [{"id": "1", "text": "A"}, {"id": "2", "text": "b"}])
# -> [{'id': '1', 'text': 'A'}, {'id': '2', 'text': 'b'}]
```

**Think first:** why use a dict from id to position instead of searching the list for every new message?

**Hint:** keep `position = {id: index}` and update it when you append a message that has an id.
