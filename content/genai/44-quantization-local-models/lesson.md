---
title: "Awareness: quantization, Ollama, vLLM and local models"
summary: Learn how to size a model's memory, what quantization does to it, how Ollama and vLLM run models on your own machine, and when local is better than hosted.
plan_ids: []
---

Until now your model lived on Groq's servers. You sent a request and got text. Sometimes you want the model **on your own machine or server**: for privacy, for cost at high volume, for no internet, or to use a fine-tuned model (lesson 43).

This is an **awareness** lesson. You learn the sizes, the trade-offs and the tools. You do not need a GPU to follow it.

## The first question: does it fit?

A model is a list of numbers called **parameters** (or weights). A "7B" model has 7 billion of them. Each number takes bits of memory:

| Format | Bits | Bytes per number |
|---|---|---|
| fp32 | 32 | 4 (training, rarely for serving) |
| fp16 / bf16 | 16 | 2 (the usual "full" quality) |
| int8 | 8 | 1 |
| int4 | 4 | 0.5 |

So:

```python
memory_gb = params_billion * bits / 8
print(7 * 16 / 8)     # -> 14.0   a 7B model in 16 bits needs 14 GB
print(7 * 4 / 8)      # -> 3.5    in 4 bits it needs 3.5 GB
print(70 * 16 / 8)    # -> 140.0  a 70B model needs several big GPUs
```

That is only the **weights**. You also need room for the **KV cache** (it grows with the context length and the number of users, GenAI lesson 2) and the runtime. A quick rule: multiply by about **1.2**, more for long contexts or many users (exercise 1).

## What is quantization?

**Quantization** stores each weight with fewer bits. A 4-bit model is about a quarter of the size of a 16-bit model. It is smaller, needs less memory, and is often faster (less data to move). The price is a small **rounding error** in every weight, so quality can drop a little.

The simplest version, **symmetric int8**:

```python
values = [12.7, -12.7, 0.0, 3.0]
scale = max(abs(v) for v in values) / 127        # -> 0.1
quantized = [round(v / scale) for v in values]   # -> [127, -127, 0, 30]
restored = [q * scale for q in quantized]        # -> [12.7, -12.7, 0.0, 3.0]
```

What just happened:

1. The biggest absolute value (12.7) is mapped to 127, the top of a signed byte.
2. Every other value is scaled the same way and rounded to a whole number. Each now fits in **one byte**.
3. To use a weight, multiply by the `scale` again. Small differences appear because of rounding.

The weakness is the **outlier**. One huge value makes `scale` large, and then small values all round to nearly the same few numbers. You see this in exercise 2. Real methods fix it by using **one scale per small group of weights** (for example per 32 or 128 values), and by clever tricks that protect the important weights.

### Step by step: quantize and measure (exercise 2)

1. Find the biggest absolute value. If it is 0, use a scale of 1.
2. `scale = biggest / 127`.
3. Divide each value by the scale and round.
4. Multiply back and compare with the original. The worst difference is your error.
5. Add an outlier to the list and watch the error grow.

## Names you will meet

- **GGUF:** a file format used by `llama.cpp` and Ollama. Names like `Q4_K_M` mean "about 4 bits, a certain method". Good for laptops and CPUs.
- **GPTQ, AWQ:** methods that quantize carefully for GPUs (they look at real data to protect the important weights). Often 4-bit.
- **bitsandbytes (NF4):** 4-bit loading used in QLoRA (lesson 43).
- **FP8:** 8-bit floating point, supported by newer GPUs.
- **PTQ vs QAT:** *post-training* quantization shrinks a trained model. *Quantization-aware training* trains with the rounding in mind, for better quality.

(These names are from memory and the field moves fast. Check the docs of the tool you use.)

## How much quality do you lose?

Rough, widely seen pattern (always test on **your** task):

| Bits | Size vs 16-bit | Quality |
|---|---|---|
| 8 | half | almost the same |
| 4 | quarter | small drop, fine for many uses |
| 3 or 2 | smaller | clearly worse, risky |

A bigger model at 4 bits often beats a smaller model at 16 bits **in the same memory**. Small models and tasks with exact answers (code, math) are hurt more. The right test: run your own eval set (GenAI lesson 41) on the quantized model and compare.

## Pick a format for your GPU (exercise 3)

Take the biggest number of bits that still fits:

```python
pick_quantization(13, 24)
# -> 8     (16 bits needs about 31 GB with overhead; 8 bits needs about 16 GB)
```

If 4 bits does not fit, the model is too big for this machine.

## The tools to run a model

| Tool | What it is | Good for |
|---|---|---|
| **Ollama** | one command to download and run a model; local server | laptops, quick experiments, local dev |
| **llama.cpp** | the C++ engine under Ollama; runs GGUF on CPU and GPU | small machines, offline |
| **vLLM** | a high-throughput inference server for GPUs; batches many requests | production serving at volume |
| **Hugging Face `transformers`** | the general Python library | research, custom code |
| **Others** | TGI, SGLang, TensorRT-LLM (check the docs for what is current) | specific needs |

Why is vLLM fast for many users? It uses **continuous batching** (new requests join a batch that is already running) and **paged attention** (it manages the KV cache in small blocks, so less memory is wasted). Those two ideas let one GPU serve many users at once.

### One API for all (exercise 4)

Ollama and vLLM can both speak the **OpenAI-compatible** API, the same `/chat/completions` request you use with Groq. Only the base URL and the key change:

```python
# Hosted:  https://api.groq.com/openai/v1   (needs your key)
# Ollama:  http://localhost:11434/v1        (no key)
# vLLM:    http://localhost:8000/v1         (no key by default)
```

The ports are the usual defaults. With the `openai` or `groq` SDK you set the base URL and use the same code. This is why you should keep model calls behind **one small function**: switching is then a config change. You can also use the router of GenAI lesson 33: easy tasks go to a cheap local model, hard ones to a big hosted one.

## Local or hosted?

| | Hosted (Groq, OpenAI, ...) | Local / self-hosted |
|---|---|---|
| Setup | one key | hardware, install, updates |
| Best models | the strongest ones | open models only |
| Cost | pay per token | pay for the machine, cheap at high steady volume |
| Privacy | data leaves your network | data stays inside |
| Speed | very fast on Groq | depends on your GPU |
| Maintenance | none | you run it, monitor it, scale it |

Rule of thumb: **start hosted**. Move to local when privacy, offline use or a high, steady volume makes it worth the work. Many teams use both.

## Try it live

1. Install Ollama (from its website). Run a small model, for example `ollama run llama3.2` (a small model name from memory; check the Ollama library).
2. Call it through the OpenAI-compatible URL with the same code you wrote for Groq. Change only `base_url` and the model name.
3. Pull the same model in two sizes or quantizations. Compare the speed and a few answers.
4. Use your `quantize` function on 1000 random numbers. Print `max_error`. Add one huge outlier and print it again.
5. Fill a table for your machine: memory, which models fit, in which format.

(No GPU? Small models run on a laptop CPU, slowly. You can also skip this step. The quizzes and exercises do not need it.)

## A little deeper

- **Memory for the KV cache:** per token it is about `2 x layers x kv_heads x head_dim x bytes`. Long contexts and many users can use more memory than the weights. This is why people quantize the KV cache too.
- **Why weights only?** Most methods quantize the weights, and keep the **activations** (the numbers flowing through) in higher precision. Some newer methods quantize both.
- **Speed is limited by memory.** To make one token the GPU reads **all** the weights. Fewer bytes to read means more tokens per second. That is why 4-bit is often faster, not only smaller.
- **Throughput vs latency.** Batching raises the tokens per second for the whole server, but each user may wait a bit longer.
- **Speculative decoding:** a small "draft" model guesses several tokens and the big model checks them at once. It speeds up generation without changing the output.
- **Licences.** Open-weight models have licences (some limit commercial use or very large companies). Read them.
- **Context length and quantization** interact: a model may be fine at 4 bits for short text and worse at very long text.

## Common mistakes

- Counting only the weights and forgetting the KV cache and runtime.
- Assuming 4-bit is always "as good". Test on your own eval set.
- Quantizing to 2 or 3 bits and wondering why answers are poor.
- Judging a local model by one prompt instead of an eval set.
- Hard-coding the Groq URL and key everywhere, so moving to local is painful.
- Running a local model for a few requests a day, where hosted is cheaper.
- Forgetting security: a local server open to the network with no key.

## Interview corner

**What is quantization and why use it?**
Storing weights with fewer bits (for example 8 or 4 instead of 16). It cuts memory and often speeds up inference, so bigger models fit on smaller hardware, at a small cost in quality.

**How much memory does a 7B model need?**
About 14 GB in 16-bit, 7 GB in 8-bit and 3.5 GB in 4-bit for the weights, plus the KV cache and runtime overhead.

**Ollama vs vLLM?**
Ollama is easy local use (laptop, development). vLLM is a high-throughput GPU server for production, with continuous batching and paged attention.

**When would you self-host?**
For privacy or compliance, offline use, a fine-tuned model, or high steady volume where owning the hardware is cheaper. Otherwise start hosted.

**How do you switch between hosted and local with little code change?**
Both can use an OpenAI-compatible API. Keep one model-call function, and set the base URL, key and model name from configuration.

**What is QLoRA?**
LoRA fine-tuning on a 4-bit quantized base model (lesson 43).

## Summary

- Weights memory in GB = billions of parameters x bits / 8. Add about 20% or more for the KV cache and runtime.
- **Quantization** stores weights in fewer bits: 8-bit is nearly free, 4-bit is usually fine, 3 or 2 bits hurts. Outliers and rounding cause the error.
- Pick the largest bit count that fits. Test the quantized model on your own eval set.
- Tools: **Ollama** and **llama.cpp** for local use, **vLLM** for serving many users (continuous batching, paged attention).
- Ollama and vLLM offer an OpenAI-compatible API, so switching is mostly a base URL change. Keep model calls in one function.
- Start hosted. Go local for privacy, offline use, fine-tuned models or high steady volume.
- Reference: `reference/genai-groq.md` (quantization and local models section).
