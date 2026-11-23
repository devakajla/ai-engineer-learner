# Check the citations

A model can invent a citation like `[7]` when only 3 chunks were given. Check them.

`extract_citations(answer)` (exercise 1) is in the starter. Write `check_citations(answer, n_hits)`.

Rules:
- `cited`: the citation numbers between 1 and `n_hits`, in the order of first appearance.
- `invalid`: the citation numbers outside that range (below 1 or above `n_hits`), in order.
- `ok`: `True` only when there is **at least one** valid citation and **no** invalid ones.
- Return `{"cited": [...], "invalid": [...], "ok": ...}`.

```python
check_citations("Use DELETE [1].", 3)       # -> {'cited': [1], 'invalid': [], 'ok': True}
check_citations("Use DELETE [1][7].", 3)    # -> {'cited': [1], 'invalid': [7], 'ok': False}
check_citations("No sources.", 3)           # -> {'cited': [], 'invalid': [], 'ok': False}
```
