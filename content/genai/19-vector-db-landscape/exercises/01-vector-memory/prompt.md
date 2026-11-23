# How much memory do the vectors need?

Write `vector_memory_mb(n_vectors, dim, bytes_per_number=4)`. It returns the memory for the raw vectors in **megabytes**, where 1 MB is 1,000,000 bytes, rounded to 2 decimal places.

Rules:
- `n_vectors * dim * bytes_per_number` is the number of bytes. Divide by `1_000_000`.
- Raise `ValueError` if any of the three numbers is negative.
- Zero vectors give `0.0`.

```python
vector_memory_mb(1_000_000, 384)         # -> 1536.0
vector_memory_mb(100_000, 768)           # -> 307.2
vector_memory_mb(1_000_000, 384, 1)      # -> 384.0      (1 byte per number: quantized)
vector_memory_mb(0, 384)                 # -> 0.0
```

**Think first:** by how much does the memory drop when each number uses 1 byte and not 4?
