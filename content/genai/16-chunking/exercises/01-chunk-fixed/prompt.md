# Fixed-size chunks with overlap

Write `chunk_fixed(text, size, overlap=0)`. It cuts `text` into pieces of at most `size` characters. Each piece starts `size - overlap` characters after the start of the one before.

Rules:
- Raise `ValueError` if `size <= 0`, if `overlap < 0`, or if `overlap >= size`.
- Stop as soon as a chunk reaches the end of the text. Do not add a last chunk that holds only text already seen.
- Empty text gives `[]`.

```python
chunk_fixed("abcdefghij", 4)        # -> ['abcd', 'efgh', 'ij']
chunk_fixed("abcdefghij", 4, 1)     # -> ['abcd', 'defg', 'ghij']
chunk_fixed("abc", 10)              # -> ['abc']
chunk_fixed("", 4)                  # -> []
```

**Think first:** by how many characters does the start move after each chunk? When do you stop?

**Hint:** a `while` loop with `start`, the slice `text[start:start + size]`, and a `break`.
