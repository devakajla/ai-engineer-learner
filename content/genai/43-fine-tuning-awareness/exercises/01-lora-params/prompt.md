# Count what LoRA trains

Full fine-tuning changes every number (weight) in the model. **LoRA** keeps the big weight matrix `W` frozen and trains two thin matrices next to it: `A` (shape `rank x d_in`) and `B` (shape `d_out x rank`). The change to the layer is `B @ A`. The smaller the **rank**, the fewer numbers you train.

Write `lora_params(d_in, d_out, rank)` for **one** weight matrix of shape `d_out x d_in`:

- `full`: the numbers in the full matrix, `d_in * d_out`.
- `lora`: the numbers in `A` and `B`, `rank * (d_in + d_out)`.
- `percent`: `100 * lora / full`, rounded to 2 decimals.

Return `{"full": ..., "lora": ..., "percent": ...}`. If `rank < 1`, raise `ValueError`.

```python
lora_params(4096, 4096, 8)
# -> {'full': 16777216, 'lora': 65536, 'percent': 0.39}
```

**Think first:** with rank 8, LoRA trains well under 1% of the numbers of this layer. Why can such a small change still teach the model a new style?

**Hint:** `A` has `rank * d_in` numbers and `B` has `d_out * rank` numbers.
