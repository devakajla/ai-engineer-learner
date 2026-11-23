# Choose the best format for your GPU

Higher bit counts keep more quality. So the rule is: use the **biggest** number of bits that fits in memory. If even 4 bits does not fit, the model is too big for this machine (choose a smaller model, or a bigger GPU).

The starter gives you `model_memory_gb` and `fits_on_gpu` (exercise 1). Write:

1. `pick_quantization(params_billion, gpu_gb, options=(16, 8, 4))`: try the options from the **largest bits to the smallest** (sort them, so any order works) and return the first one where `fits_on_gpu(params_billion, bits, gpu_gb)` is true. Return `None` if none fits.
2. `plan(models, gpu_gb)`: `models` is a dict `{name: size in billions}`. Return a dict `{name: pick_quantization(size, gpu_gb)}`.

```python
pick_quantization(13, 24)
# -> 8     (16 bits needs about 31 GB, 8 bits needs about 16 GB)
plan({"small": 3, "large": 70}, 24)
# -> {'small': 16, 'large': None}
```

**Think first:** why is 8-bit often "almost free" in quality, while 3-bit or 2-bit often is not?

**Hint:** `sorted(options, reverse=True)` and an early `return` inside the loop.
