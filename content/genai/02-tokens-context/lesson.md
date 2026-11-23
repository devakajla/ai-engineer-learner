---
title: Tokens and the context window
summary: Learn what a token is, how to estimate tokens and cost, why every model has a limit on how much text it can handle at once, and why long input is slow.
plan_ids: []
---

In lesson 1 we said an LLM predicts the next "word". That was a small simplification. A model does not read words. It reads **tokens**.

Tokens matter a lot in real work, for three reasons:

1. They decide **what you pay**.
2. They decide **how much text fits** in one call.
3. They decide **how fast** the answer comes back.

## What is a token?

A computer cannot read letters the way you do. It works with numbers. So before the model sees your text, the text is cut into small pieces, and each piece gets a number. A piece is a **token**.

A token can be a whole word, part of a word, a space, or a punctuation mark.

A rough picture (the exact cut depends on the model):

```
"hello"          -> 1 token
"hello world"    -> 2 tokens
"unbelievable"   -> a few tokens, like "un" + "believ" + "able"
"नमस्ते"           -> several tokens (other languages often need more)
```

The program that cuts text into tokens is called a **tokenizer**. Each model family has its own tokenizer. So the same text can have a different token count in different models.

Rules of thumb for English:

- 1 token is about **4 characters**.
- 100 tokens is about **75 words**.
- One page of text is about 500 tokens.

These are estimates, not exact numbers.

## Estimating tokens in code

A quick estimate: take the number of characters, divide by 4, and **round up**.

Rounding up with whole numbers is a small trick. Add `divisor - 1` first, then use `//`. The `//` operator divides and drops the decimal part.

Let's learn the trick with a different example. A page holds 10 lines. How many pages do `n` lines need?

1. 25 lines is 2.5 pages. You need 3 pages, so you must round **up**.
2. Add 9 to the lines: `25 + 9 = 34`.
3. Use `//` with 10: `34 // 10 = 3`.

```python
def pages_needed(lines):
    return (lines + 9) // 10

pages_needed(25)   # -> 3
pages_needed(20)   # -> 2
pages_needed(0)    # -> 0
```

Why does this work? Adding 9 pushes any leftover over the next whole number. A leftover of 1 line (21 lines) becomes 30, which gives 3. An exact fit (20 lines) becomes 29, which still gives 2.

You will use the same trick for tokens. You do not need exact counts for planning. The API tells you the real count after every call (lesson 3).

## The context window

A model can only handle a limited amount of text in one call. That limit is the **context window**. It is counted in tokens.

Everything counts toward it:

- Your instructions.
- The documents you send.
- The chat history.
- **The answer the model writes.**

```
context window = input tokens + output tokens
```

Think of a desk. The desk has a fixed size. Your papers (input) and the paper the model is writing on (output) must both fit on it. Anything that does not fit is not on the desk, so the model cannot see it.

A model with 131,072 tokens (about 100,000 words) has a big window. Older models had 4,000. Look up the real number for your model on `console.groq.com/docs/models`.

If the input is too long, the API gives an error. So check **before** you call:

```python
def can_send(input_tokens, max_output, limit):
    return input_tokens + max_output <= limit

can_send(1000, 500, 4096)    # -> True
can_send(4000, 500, 4096)    # -> False
```

Look at `<=`. Using exactly the whole window is allowed.

The window is the model's **short-term memory**. Your documents are much bigger than one window. That is why we need tricks like RAG later.

## Tokens and money

Providers charge **per token**. Prices are given **per 1 million tokens**. **Input** tokens (what you send) and **output** tokens (what the model writes) have different prices. Output usually costs more.

```
cost = tokens / 1,000,000 * price_per_million
```

Python lets you write big numbers with underscores: `1_000_000` is the same as `1000000`.

```python
def input_cost(tokens, price_per_million):
    return tokens / 1_000_000 * price_per_million

input_cost(2_000_000, 0.5)    # -> 1.0
input_cost(1_000, 0.5)        # -> 0.0005
```

For one call, work out the input cost and the output cost separately, then add them. Prices change, so read the current price on the provider's site. Do not memorise prices.

## Why long input makes a call slow

Cost is not the only thing that grows with input. **Time** grows too.

Before the model writes its first word, it must read all your input. A long input means a longer wait for the first word. This wait is the **time to first token** (TTFT).

Then the model writes the answer **one token at a time**. Each new token needs a pass through the model. That is why output is slower, and often costs more, than input.

To save work, the model keeps notes about the text it has already read. These notes are the **KV cache** (key-value cache). The model does not re-read the whole text for every new token. It reuses its notes.

Think of reading a long contract. You read it once and make notes. When someone asks a question, you look at your notes. You do not read the whole contract again for every question.

Two things follow:

- A bigger context means bigger notes, so it needs more computer memory and time.
- Some providers can reuse the notes between calls when the **start** of your prompt is the same. This is called **prompt caching**. It makes repeated long prompts cheaper and faster. You will meet it again when we talk about cost.

## Try it live

In the Groq Playground, send a short question and a long question (paste a few paragraphs). Compare how long the first word takes. Then, after lesson 3, read `response.usage` in code and see the real token counts for both.

## A little deeper

- **Why the odd cuts?** Most models learn a fixed list of common pieces from their training text (a method called **BPE**, byte pair encoding). Common words become one token. Rare words are cut into several pieces.
- **Why models fail at counting letters.** The model sees tokens, not letters. "How many r's in strawberry?" is hard, because the word is a few chunks, not ten separate letters.
- **Other languages and code.** Hindi, and text with many symbols, often use more tokens for the same meaning. So they cost more and fit less.
- **Max output is a separate limit.** A model also caps how long one answer can be. That cap is smaller than the context window.
- **Rate limits use tokens too.** Providers often limit you to a number of tokens per minute, not only a number of requests.
- **Long contexts get fuzzy.** Even inside the window, models can miss details hidden in the middle of very long input. Sending less, but better, text is often the best choice.

## Common mistakes

- Forgetting that the **answer** also uses the window.
- Mixing up input and output prices.
- Treating `len(text)` as the token count. It counts characters.
- Using `/` and getting `2.5` when you needed a whole number (use `//`).
- Sending a whole book "because it fits". It costs money and slows the call.

## Interview corner

**What is a token?**
A piece of text the model reads, like a word or part of a word. About 4 characters in English.

**What is the context window?**
The most tokens a model can handle in one call. Input and output both count.

**How do you control LLM cost?**
Send less text, pick a smaller model for easy tasks, set `max_completion_tokens`, cache repeated answers, and track token usage per call.

**Why does the same text cost different amounts in different languages?**
Tokenizers are tuned for common languages like English. Other languages are cut into more tokens, so they cost more.

**What is a KV cache?**
Notes the model keeps about text it has already read, so it does not re-read everything for each new token. It makes generation faster, but it uses memory that grows with context length.

## Summary

- A model reads tokens, not words. About 4 characters, or 0.75 words, in English.
- Context window = input tokens + output tokens. Go over it and the call fails.
- Round-up division: `(n + k - 1) // k`.
- Cost = tokens / 1,000,000 * price per million. Input and output are priced separately.
- Long input is slow (time to first token). The KV cache and prompt caching reduce repeated work.
- Reference: `reference/genai-groq.md`.
