---
title: "Awareness: fine-tuning, LoRA and QLoRA"
summary: Learn what fine-tuning changes, when to use it (and when prompting or RAG is better), how LoRA and QLoRA make it cheap, and how training data and checks work.
plan_ids: []
---

Every LLM job interview asks: "Would you fine-tune a model for this?" The best answer is usually "not yet". This lesson gives you the map: what fine-tuning is, the cheap method (LoRA), what the data looks like, and a clear rule for when to do it.

This is an **awareness** lesson. You will not train a model today. You will learn the ideas well enough to explain and to decide.

## What fine-tuning changes

A model is a huge set of numbers called **weights**. **Pre-training** set them using a large part of the internet (GenAI lesson 32). **Fine-tuning** continues training on a small set of your own examples, so the weights change a little.

What this is good for:

- **Style and format:** "always answer in our brand voice", "always return this JSON shape".
- **A narrow skill:** classify support tickets into 12 labels, extract fields from invoices.
- **Making a small model act like a bigger one** on one task (cheaper and faster to run).

What it is **bad** for:

- **Adding facts.** A model that is trained on your price list may still make up a price. Facts change. Weights are hard to update. Use RAG.
- **Fixing a bad prompt.** Try a better prompt and examples first.
- **Fast change.** Training takes hours and an evaluation. A prompt changes in seconds.

## The ladder: prompt, RAG, then fine-tune

```
1. Prompt        write clear instructions + few-shot examples      (minutes, free)
2. RAG           give the model the facts at question time         (days)
3. Fine-tune     change the model's habits with examples           (weeks, needs data)
```

Move up only when the lower step fails. In exercise 2 you write this as a small decision function.

> **Interview answer:** "I would first try prompting with examples, then RAG for knowledge. I would fine-tune only for a style or a narrow task, with at least some hundreds of good examples, and a test set to prove it helps."

## Full fine-tuning vs LoRA

**Full fine-tuning** trains every weight. A 7-billion-weight model needs a lot of GPU memory, because you store the weights and the training bookkeeping for every one of them.

**LoRA** (Low-Rank Adaptation) is the trick that made fine-tuning cheap. Think of a huge matrix `W` in the model. Instead of changing `W`, you **freeze** it and add two thin matrices next to it:

```
output = W x  +  B (A x)
         ^frozen  ^trained, small
A: rank x d_in      B: d_out x rank       (rank is small, like 8 or 16)
```

The change to the layer is `B @ A`. Because the **rank** is small, `A` and `B` hold very few numbers:

```python
d_in = d_out = 4096
rank = 8
full = d_in * d_out              # -> 16777216
lora = rank * (d_in + d_out)     # -> 65536
print(round(100 * lora / full, 2))
# -> 0.39      (percent of the numbers you train)
```

So you train about **0.4%** of the numbers of that layer. The result is a small file (the **adapter**, often tens of MB). You keep one big base model and many small adapters, one per task or per customer. In exercise 1 you compute these numbers.

Why does a tiny change work? Fine-tuning for a style or task usually needs only a small, "low-rank" change to what the model already knows. It is steering, not teaching from zero.

## QLoRA

**QLoRA** = LoRA + a **quantized** base model. Quantization (lesson 44) stores the frozen weights in 4 bits instead of 16, so a 7B model shrinks from about 14 GB to about 4 GB. The adapters are still trained in higher precision. The result: you can fine-tune a 7B model on one consumer GPU. The price is a bit of quality and extra care.

## Other training words you will hear

- **SFT** (supervised fine-tuning): learn from "input, ideal output" pairs. This is what this lesson is about.
- **RLHF / DPO**: learn from **preferences** ("answer A is better than B"). Used to make models helpful and safe (GenAI lesson 32). DPO is the simpler method that skips the separate reward model.
- **Distillation:** a small model learns to copy a big model's answers.
- **Continued pre-training:** train on a lot of raw text from a field (law, medicine) to teach vocabulary. Rare and expensive.

## The data

The data is the work. A typical SFT file is **JSONL**: one example per line, in the chat format:

```json
{"messages": [{"role": "system", "content": "You write short answers."},
              {"role": "user", "content": "What is HTTP 404?"},
              {"role": "assistant", "content": "Not Found: the page does not exist."}]}
```

Rules of thumb:

- **Quality beats quantity.** A few hundred clean, consistent examples can beat thousands of messy ones.
- **Examples must look like real use.** Same kind of inputs, same format of output.
- **Check every line** (exercise 3): valid JSON, a user message, the last message from the assistant, no empty text.
- **Hold out a validation set** (exercise 4). Never evaluate on examples the model trained on. Split by a **hash** of the example so the split stays the same when you add data, and no example sits in both sets.
- **Remove private data** (names, keys) before training. A model can repeat what it saw.

### Step by step: a stable split (exercise 4)

1. For one example, compute a number from its text with a hash (`md5`), then take `% 100`. The same text always gives the same number.
2. If the number is below `val_fraction * 100`, the example goes to validation. Otherwise to training.
3. Loop over all examples and fill two lists.
4. Check: nothing lost, nothing in both, and adding new data does not move old examples.

## How you know it worked

1. Before training, run your **base model with a good prompt** on the validation set. Score it. This is the number to beat.
2. After training, run the **fine-tuned model** on the same set with the same scoring (exact match, a rubric, an LLM judge as in GenAI lesson 41).
3. Check for **forgetting**: also test a few general tasks. Fine-tuning can make a model worse at things you did not train.
4. Compare the **cost and speed**, too. A small fine-tuned model can replace a big prompted one.

If the fine-tuned model does not beat the prompted baseline, you wasted the effort. This check is what interviewers want to hear.

## Where you would do it

- **Hosted fine-tuning** by a model provider: you upload a JSONL file, they train, you call a new model name. Not every provider or model offers it. Check the docs of your provider.
- **Open tools** such as Hugging Face `transformers`, `peft` (LoRA) and `trl` (SFT trainers), or ready tools like Unsloth. The code is short. The hard part is the data and the evaluation. (These names are from memory. Check the current docs.)
- **Local or rented GPU** for QLoRA.

## Try it live

No training is needed.

1. Pick one task from your life (for example, turn a messy note into a clean to-do list).
2. Write a prompt with 3 examples. Test it on 10 inputs. Count how many are good.
3. Write 20 examples in the JSONL format by hand. Run your `check_example` on every line.
4. Split them with `split_dataset`. Write down what score a fine-tuned model would have to beat.
5. Answer: "Is fine-tuning worth it here? What would change my mind?"

## A little deeper

- **Rank and alpha.** Besides `rank`, LoRA has `alpha` (a scale for the update) and a list of which layers get adapters (often the attention layers). Higher rank means more capacity and more memory.
- **Merging.** You can merge the adapter into the base weights for fast serving, or keep it separate to switch adapters per request.
- **Catastrophic forgetting.** Too many steps or too high a learning rate overwrite old skills. Use a low learning rate, few epochs, and test general skills.
- **Overfitting.** The model repeats the training examples. A validation set that keeps getting worse is the sign.
- **Synthetic data.** A strong model can write training examples for a small one. Always review a sample by hand.
- **Reasoning models and RL.** Newer models are trained with reinforcement learning on tasks with checkable answers. This is a different, bigger topic.

## Common mistakes

- Fine-tuning to add facts that RAG should supply.
- Fine-tuning before trying a better prompt and few-shot examples.
- No baseline. You cannot say the model improved.
- Testing on training examples.
- Too few or inconsistent examples.
- Leaving private data in the training file.
- Forgetting to check that general skills did not get worse.

## Interview corner

**When would you fine-tune instead of using RAG or prompting?**
For style, format or a narrow task when prompts fail and I have enough clean examples. For knowledge I use RAG, because facts change and weights are hard to update.

**What is LoRA?**
Freeze the big weights and train two small low-rank matrices per layer. The update is their product. It trains well under 1% of the numbers and gives a small adapter file.

**What is QLoRA?**
LoRA on a 4-bit quantized base model. It cuts memory so a 7B model can be tuned on one GPU, with a small quality cost.

**How do you check a fine-tune helped?**
Score the base model with a good prompt on a held-out validation set, score the tuned model the same way, and also test general tasks for forgetting.

**SFT vs RLHF/DPO?**
SFT learns from ideal answers. RLHF and DPO learn from preferences between answers, to shape helpfulness and safety.

## Summary

- Fine-tuning changes weights with your examples. Use it for **style, format and narrow skills**, not for facts.
- Ladder: **prompt, then RAG, then fine-tune**.
- **LoRA** freezes the model and trains small low-rank matrices (`rank * (d_in + d_out)` numbers). **QLoRA** adds a 4-bit base.
- Data is JSONL chat examples. Quality beats quantity. Check each line, remove private data, and keep a stable validation split.
- Always compare with a prompted baseline, and test for forgetting.
- Reference: `reference/genai-groq.md` (fine-tuning section).
