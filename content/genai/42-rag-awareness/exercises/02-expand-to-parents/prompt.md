# Small chunks to find, big chunks to read

**Parent-child retrieval**: search small chunks (precise matching), but give the model the bigger **parent** section they belong to (complete context).

Write `expand_to_parents(hits, parent_of, parents)`.

- `hits`: a list of `{"id", "text", "score"}`, best first.
- `parent_of`: a dictionary `{child_id: parent_id}`. A hit that is not in it has no parent.
- `parents`: a dictionary `{parent_id: parent_text}`.

Return a list of `{"id", "text", "score"}`, one per **different** parent:
- A hit with a parent becomes `{"id": parent_id, "text": parents[parent_id], ...}`.
- A hit without a parent stays as itself (its own id and text).
- If several hits share a parent, return that parent **once**, in the position of its **first** hit, with the **highest** score of its children.

```python
hits = [{"id": "c1", "text": "t1", "score": 0.5}, {"id": "c2", "text": "t2", "score": 0.9}]
expand_to_parents(hits, {"c1": "p", "c2": "p"}, {"p": "whole section"})
# -> [{'id': 'p', 'text': 'whole section', 'score': 0.9}]
```
