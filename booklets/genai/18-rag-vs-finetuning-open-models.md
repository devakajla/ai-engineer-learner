# 18. Prompting, RAG or fine-tuning? Open models and fine-tuning basics

A very common interview question: "the model does not do what we want. What do you change?" The answer is a **ladder**, from cheap to costly. Climb only as far as you must.

## The ladder

@@ vflow | Figure 18.1: try these in order.
1. Better prompt|clear instructions, examples, format|green -> 2. Add RAG|give it the facts at question time|blue -> 3. Add tools|let it fetch live data or act|yellow -> 4. Fine-tune|change the model's behaviour itself|red
@@ end

| Problem | Best first tool |
| --- | --- |
| wrong format or tone | prompt (system message, few-shot examples) |
| does not know my data | **RAG** |
| facts change every day | RAG (re-index), not fine-tuning |
| needs live numbers or actions | tools |
| must follow a style or format that prompts cannot hold reliably | fine-tuning |
| too slow or expensive at scale, a small model could do it | fine-tune a small model |
| must cite sources | RAG |

**Key rule:** fine-tuning teaches **behaviour and style**, not facts. Do not fine-tune to "add knowledge". It is expensive, forgets, goes stale, and the model may still make up facts. Use RAG for knowledge.

## Long context vs RAG

Models now accept very long inputs. Why not paste all documents into the prompt?

| Long context | RAG |
| --- | --- |
| simple, no index to build | needs ingestion and retrieval |
| every request pays for all the tokens | pays only for retrieved chunks |
| slower, and the model can lose details in the middle | focused context |
| fine for a few documents | needed for thousands of documents |
| no easy citations | citations come naturally |

Use long context for a **single or a few documents**. Use RAG for **big or changing collections**. Many systems combine them: RAG to pick the documents, long context to read them.

## Open-source models

Besides API models, you can run **open-weight** models (Llama, Mistral, Qwen, Gemma and others) yourself.

| Reason to self-host | Reason not to |
| --- | --- |
| data must stay inside | needs GPUs, and people to run them |
| predictable cost at huge volume | API is cheaper at low volume |
| full control, fine-tuning freedom | the best closed models may be stronger |
| no vendor lock-in | you own uptime, scaling and updates |

Tools you should recognise:

- **Hugging Face:** the hub for models and datasets, and the `transformers` library.
- **Ollama:** run models on your laptop with one command. Great for learning and offline use.
- **vLLM:** a high-throughput server for production, with batching and efficient memory use.
- **llama.cpp:** runs quantised models on CPUs and small machines.

(None of these were run for this booklet. Install steps and model names change, so check each project's page.)

### Quantization

A model is a huge set of numbers (**weights**). Normally each takes 16 bits. **Quantization** stores each in fewer bits (8 or 4), so the model gets **smaller and faster**, with a small loss in quality.

A rough size rule: parameters times bytes per weight.

```python
params = 7_000_000_000          # a 7B model
for bits in (16, 8, 4):
    gigabytes = params * bits / 8 / 1e9
    print(bits, "bit ->", round(gigabytes, 1), "GB")
# -> 16 bit -> 14.0 GB
# -> 8 bit -> 7.0 GB
# -> 4 bit -> 3.5 GB
```

So a 7 billion parameter model needs about 14 GB at 16 bits, but about 3.5 GB at 4 bits, which fits on a normal laptop. (This counts the weights only. Running needs extra memory for the context.)

## Fine-tuning basics

**Fine-tuning** means training an existing model a bit more, on your own examples, so its behaviour changes.

### Instruction tuning and your data

You prepare **pairs** of input and the ideal output, often a few hundred to a few thousand. Quality matters far more than quantity. The format is usually a list of chat messages:

```python
example = {
    "messages": [
        {"role": "system", "content": "You classify support emails."},
        {"role": "user", "content": "My card was charged twice."},
        {"role": "assistant", "content": "billing"},
    ]
}
```

### Full fine-tuning vs LoRA

Updating every weight of a large model needs a lot of GPU memory. **LoRA** (Low-Rank Adaptation) freezes the original weights and trains **small extra matrices** added on top. Only a tiny share of numbers (often under 1 percent) is trained, so it is much cheaper, and the result is a small "adapter" file you can switch on or off. **PEFT** (Parameter-Efficient Fine-Tuning) is the family name for such methods, and the Hugging Face `peft` library implements LoRA. **QLoRA** does LoRA on a quantised model, to fit even bigger models on small GPUs.

@@ grid 3 | Figure 18.2: kinds of training.
Pre-training|read the internet;learn language and facts;done by model makers|gray
Instruction tuning|learn to follow tasks;from example pairs;this is what you may do|blue
RLHF and similar|learn from human preferences;makes answers helpful and safe;done by model makers|purple
@@ end

**RLHF** (Reinforcement Learning from Human Feedback) trains the model using human rankings of answers. Newer methods such as DPO reach the same goal more simply. You need to understand the idea for interviews. You will rarely run it yourself.

### When fine-tuning is worth it

- You have **hundreds of good examples** of the exact behaviour.
- A prompt with examples is too long, costly, or unreliable.
- You want a **small, cheap** model to copy a big model's skill on one narrow task.
- Always **evaluate** (chapter 16) the tuned model against the plain model with a good prompt. Often the prompt wins.

::: {.box .checkpoint}
**Checkpoint:** you can place a given problem on the ladder, and explain in two sentences why fine-tuning is the wrong way to add knowledge.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Fine-tuning to teach facts that change.
- Fine-tuning before trying a good prompt and RAG.
- Training on a few noisy examples.
- Comparing a tuned model with a badly prompted baseline.
- Forgetting that self-hosting means you run the servers.
- Ignoring licences of open models.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Prompting, RAG or fine-tuning?** Start with prompting. Use RAG for private or changing knowledge. Use fine-tuning for behaviour, style or format, or to make a small model cheap on one task.

**Q: Why not fine-tune to add knowledge?** It is costly, gets stale, may not be recalled reliably, and gives no citations. RAG is cheaper and updatable.

**Q: Long context or RAG?** Long context for a few documents. RAG for large or changing corpora, cost control and citations.

**Q: What is LoRA?** Freeze the base model and train small low-rank matrices as an adapter. Far cheaper than full fine-tuning.

**Q: What is quantization?** Storing weights in fewer bits to cut memory and speed up inference at a small quality loss.

**Q: Ollama vs vLLM?** Ollama is easy local use. vLLM is a production serving engine with high throughput.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. For each case choose prompt, RAG, tools or fine-tuning: (a) answers in a company's tone, (b) today's stock price, (c) questions on 3,000 internal PDFs, (d) must output a strict label set.
2. Compute the weight memory of a 13B model at 16, 8 and 4 bits.
3. Write five training examples in the chat format for a task of your choice.
4. Install Ollama (optional) and run a small model. Compare its answer with an API model on three questions.
5. **Think:** your company policy changes weekly. Why is RAG a better fit than fine-tuning?
:::
