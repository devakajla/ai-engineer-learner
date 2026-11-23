---
title: Chat memory
summary: Keep long chats under control - trim old messages by count or by token budget, and summarize old turns so the model still remembers them.
plan_ids: []
---

In lesson 4 you saw that the model remembers nothing, so you send the whole history each time. That has two problems:

1. **Cost and speed.** Every turn sends more tokens than the turn before.
2. **The limit.** One day the history is bigger than the context window (lesson 2), and the call fails.

**Chat memory** means deciding **what to keep** from a long conversation. There are three tools: trim by count, trim by budget, and summarize.

## 1. Keep the last N messages

The simplest idea: keep only the newest `n` messages. In Python, a **negative slice** takes from the end:

```python
history = ["a", "b", "c", "d", "e"]

print(history[-2:])   # -> ['d', 'e']       (the last 2)
print(history[-10:])  # -> ['a', 'b', 'c', 'd', 'e']   (fewer than 10 exist: you get all of them)
```

But watch out for a trap. What about `n = 0`?

```python
print(history[-0:])   # -> ['a', 'b', 'c', 'd', 'e']
```

`-0` is the same as `0`, so `history[-0:]` means "from the start" and gives **everything**. You wanted nothing. So handle small `n` yourself:

```python
def last_n(items, n):
    if n <= 0:
        return []
    return items[-n:]

last_n(["a", "b", "c"], 2)   # -> ['b', 'c']
last_n(["a", "b", "c"], 0)   # -> []
```

A slice also makes a **new list**, so the original is not changed.

> Chat messages come in pairs: a user message, then an assistant message. If you cut in the middle of a pair, the model sees an answer with no question. Keeping an **even** number of messages, or making sure the first kept message is a `user` message, avoids this.

## 2. Keep what fits a token budget

"Last 10 messages" is not very exact: ten long messages can be huge, and ten short ones tiny. A better rule: keep as many of the **newest** messages as fit in a **token budget**.

Use the estimate from lesson 2: about 4 characters per token, rounded up.

```python
def estimate_tokens(text):
    return (len(text) + 3) // 4
```

The plan:

1. Walk through the history from the **newest** to the **oldest**. `reversed(history)` does that without changing the list.
2. Keep a running `total` of tokens.
3. If adding this message would go over the budget, **stop**.
4. Otherwise keep it, and add its tokens to the total.
5. The kept messages are in newest-first order, so reverse them back with `.reverse()`.

```python
def trim_words(words, budget):
    kept = []
    total = 0
    for word in reversed(words):
        if total + len(word) > budget:
            break
        kept.append(word)
        total += len(word)
    kept.reverse()
    return kept

trim_words(["aa", "bbbb", "cc", "dd"], 6)   # -> ['cc', 'dd']
```

Let's check by hand. From the end: `dd` (2, total 2), `cc` (2, total 4), then `bbbb` would make 8, which is over 6, so stop. The kept list is `["dd", "cc"]`, and after `.reverse()` it is `["cc", "dd"]`.

Two details:

- `break` stops the loop at the **first** message that does not fit. We do not skip it and keep an even older, smaller one. A conversation with holes makes no sense.
- `.reverse()` changes the list in place and returns `None`. Do not write `kept = kept.reverse()`.

In the exercise you do the same, with `message["content"]` and `estimate_tokens`.

The system message is **not** part of the history in our app (lesson 4), so trimming never removes it. Good.

## 3. Summarize old messages

Trimming **forgets**. If the user said their name 30 messages ago, it is gone.

A **summary memory** keeps the important facts in a few sentences:

1. Split the history into **old** and **recent** parts.
2. Ask the model to summarize the old part.
3. The new history is: one message that holds the summary, then the recent messages.

```python
history = [m1, m2, m3, m4, m5, m6]   # keep_last = 2

old = [m1, m2, m3, m4]        # to summarize
recent = [m5, m6]             # kept as they are
new_history = [summary_message, m5, m6]
```

How do you split? The tempting way is `history[:-keep_last]`. But with `keep_last = 0` that is `history[:-0]`, which is `[]`: the same `-0` trap. A safer way is to compute the cut point:

```python
cut = len(history) - keep_last
old = history[:cut]
recent = history[cut:]
```

With `keep_last = 0`: `cut` is `len(history)`, so `old` is everything and `recent` is empty. 

To send the old messages to the model, turn them into a text transcript:

```python
old = [{"role": "user", "content": "I am Dev"}, {"role": "assistant", "content": "Hi Dev!"}]
transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old)
print(transcript)
# -> user: I am Dev
# -> assistant: Hi Dev!
```

Then ask: `"Summarize this conversation in 2 sentences:\n" + transcript`. The reply becomes the summary message:

```python
{"role": "user", "content": "Summary of the earlier chat: Dev introduced himself."}
```

If the history is already short (`len(history) <= keep_last`), do nothing and do **not** call the model: a call costs money.

## Which one to use?

| Method | Good | Bad |
| --- | --- | --- |
| Last N messages | Very simple, free | Forgets early facts, N is not exact |
| Token budget | Fits the limit exactly | Still forgets |
| Summary | Keeps key facts | Costs an extra model call, can lose details |
| Both: summary + recent | Best for long chats | Most code |

Many apps combine them: summarize when the history gets long, and keep a budget as a safety net.

## Summarize only when needed

A summary costs a model call. So do not make one on every turn. First **measure**. If the history still fits the budget, do nothing. Only when it is too big, summarize.

Let's practise the pattern with a different example: a notebook that gets cleaned up only when it is full.

1. Count the size (here: the number of lines).
2. If it is small enough, return a copy and stop.
3. Otherwise clean it, and check the size again.

```python
def tidy(notes, max_lines):
    if len(notes) <= max_lines:
        return list(notes)          # small enough: no work
    shorter = notes[len(notes) - 2:]   # keep the last 2 lines
    return shorter[-max_lines:]        # and make sure it fits

tidy(["a", "b"], 5)              # -> ['a', 'b']
tidy(["a", "b", "c", "d"], 5)    # -> ['c', 'd']
```

The same shape works for chat memory: measure, return early if it fits, else summarize, then trim as a safety net. You build it in the fourth exercise.

## Try it live

1. Make a chat of 12 short turns with your real model. After each turn print the number of tokens in `response.usage.prompt_tokens`. Watch it grow.
2. In turn 3 say *"My name is Asha."* Keep only the last 4 messages and ask *"What is my name?"* in turn 12. What does the model say?
3. Now summarize the old part (with your `summarize_old`) and ask again. Does it remember?

## A little deeper

- **Memory is not only history.** Apps also store **facts** about the user ("prefers short answers") in a database, and add them to the system prompt. That is long-term memory.
- **Retrieval memory.** For very long histories, store every message in a vector database (Level 3), and fetch only the old messages that are *relevant* to the new question. It is RAG applied to chat.
- **Summaries drift.** Summarizing a summary again and again loses details. Keep some raw recent messages, and re-summarize from the older raw text when you can.
- **Exact token counts.** The `usage` in a response tells you how many tokens the **last** call really used. Use it to decide when to trim, instead of only guessing.
- **Cache-friendly order.** Providers can cache a repeated start of a prompt, so keeping the early part stable (system prompt, summary) can lower cost. Cutting from the front each turn changes the start every time.
- **Do not trim tool results blindly.** An assistant message with tool calls must stay together with its tool messages, or the API gives an error.
- **Security.** A summary written by a model from user text can carry a prompt injection forward. Treat it as data.

## Common mistakes

- `history[-n:]` with `n = 0`: it returns everything.
- `history[:-keep]` with `keep = 0`: it returns nothing.
- Cutting in the middle of a user and assistant pair.
- `kept = kept.reverse()`: it sets `kept` to `None`.
- Summarizing on every single turn. It costs a model call each time. Summarize only when the history is long.
- Trimming the system message away.

## Interview corner

**How do you handle a conversation that is longer than the context window?**
Trim old messages (by count or token budget), summarize old turns into a short message, or store messages in a vector store and retrieve the relevant ones. Often a mix: a summary plus the most recent turns.

**What are the trade-offs of summary memory?**
It keeps key facts in few tokens, but costs an extra call, can drop details, and can drift when it is summarized repeatedly.

**Why is "keep the last 10 messages" a weak rule?**
Messages differ in length, so it does not control tokens. A token budget is more exact.

**What is the difference between short-term and long-term memory in an LLM app?**
Short-term is the history sent in the current call. Long-term is stored outside (a database or vector store) and fetched back when it is needed.

## Summary

- The model has no memory. You decide what to send each time.
- `items[-n:]` keeps the last `n`, but `n = 0` returns everything. Handle it.
- Token budget: walk from the newest, stop at the first message that does not fit, then `.reverse()`.
- Summary memory: summarize the old part, keep the recent part. Compute the cut point to avoid the `-0` trap.
- Do not call the model for a summary when the history is already short.
- Project: step 7 adds trimming and a summary to Copilot's chat.
- Reference: `reference/genai-groq.md`.
