# Find the citations

A cited answer looks like: `"Use DELETE [1]. You need a token [2][1]."` Your code must read the numbers.

Write `extract_citations(answer)`. It returns the numbers that appear as `[n]`, as a list of `int`.

Rules:
- A citation is `[` + digits only + `]`. `[a]`, `[]` and `[1a]` are **not** citations.
- Each number appears **once**, in the order of its first appearance.
- No citations gives `[]`.
- Do not use the `re` module. Scan the text with `find`, as in the lesson.

```python
extract_citations("Use DELETE [1]. You need a token [2][1].")   # -> [1, 2]
extract_citations("No sources here, only [a] and [].")          # -> []
```

**Think first:** what if the text has `[` but never a closing `]`?
