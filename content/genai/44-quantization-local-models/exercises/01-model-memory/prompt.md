# Will the model fit in memory?

A model is a big list of numbers (**parameters**, also called weights). Each number takes some **bits** of memory: 16 bits in the usual format (fp16 or bf16), 8 bits or 4 bits after **quantization**. 8 bits make 1 byte. So:

> memory in GB = parameters in billions x bits / 8

A 7B model in 16 bits needs `7 x 16 / 8 = 14` GB just for the weights. You need extra room for the **KV cache** (GenAI lesson 2) and for the runtime. A simple rule is to multiply by an **overhead** of about 1.2.

Write:

1. `model_memory_gb(params_billion, bits)`: the weights memory in GB.
2. `fits_on_gpu(params_billion, bits, gpu_gb, overhead=1.2)`: `True` if `model_memory_gb(...) * overhead <= gpu_gb`.

```python
model_memory_gb(7, 4)
# -> 3.5
fits_on_gpu(13, 16, 24)
# -> False   (26 GB of weights, about 31 GB with overhead)
```

**Think first:** a 24 GB GPU cannot run a 13B model in 16 bits, but can in 4 bits. What do you pay for that?

**Hint:** one line each. Remember `<=`: an exact fit works.
