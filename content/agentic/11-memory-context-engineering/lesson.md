---
title: "Memory and context engineering"
summary: Give an agent long-term memory (save, recall, extract facts), keep the prompt small with summaries and budgets, and learn the four moves of context engineering.
plan_ids: []
---

A model has no memory. Each call starts empty. In lesson 9 you saw the **short-term** fix: the checkpointer saves the messages of one thread. That is not enough for a good assistant:

- The user comes back next week in a **new** thread. The assistant should still know their name and taste.
- A long thread grows. Tokens cost money, and a stuffed prompt makes the model **worse**, not better.

This lesson covers both: **long-term memory** (facts that last) and **context engineering** (choosing what goes into the prompt).

## Kinds of memory

| Kind | What it holds | Where it lives |
|---|---|---|
| Short-term | the messages of one conversation | checkpointer (lesson 9) |
| Long-term, facts | "Dev lives in Pune", "prefers short answers" | a store, per user |
| Long-term, events | "last week we fixed the login bug" | a store, with dates |
| Long-term, rules | "always answer in English" | the system prompt |

In LangGraph a **store** is a key-value place shared by all threads (check the docs for the current `Store` API). The idea is simple. You can build it with a dict.

## Save and recall facts

```python
store = {}                      # {user_id: [fact, fact, ...]}
store.setdefault("u1", []).append("Dev likes strong tea")
```

To use a fact you must **find** it. With thousands of facts you cannot put all of them in the prompt. You **recall** only the few that match the new question. A first version counts shared words. A better version uses embeddings (GenAI lesson 14), the same search you built for RAG. Memory is just RAG over what the user said before.

```python
words = set("strong tea please".split())
fact = "Dev likes strong tea"
print(len(words & set(fact.lower().split())))
# -> 2
```

### Step by step: save and recall (exercise 1)

1. `save_fact`: get the user's list with `setdefault`. If the fact (lower case, trimmed) is already there, return `False`. Else append it and return `True`.
2. `recall`: turn the query into a set of lower-case words.
3. For each fact, count how many query words it shares. Keep it only if the count is above 0.
4. Sort by count, highest first. Return the first `k`.
5. Test: duplicates, two users, no match.

## Let the model choose what to remember

You do not want to save "hello" or "thanks". A cheap model call can **extract** the lasting facts:

```python
reply = ask(client, "List the lasting facts about the user in this message as a JSON list ...\n\n" + message)
# -> '["Dev lives in Pune", "Dev likes Python"]'
```

Then you parse the JSON. The model might add words or a code fence, or return nonsense. So you cut from the first `[` to the last `]`, parse with `try/except`, and return `[]` on any problem. This is the "validate model output" habit from GenAI lesson 9, applied to memory. Bad memory is worse than no memory: a wrong fact will be repeated for months.

> **Privacy.** Saved facts are personal data. Tell users what you keep, let them see and delete it, and never save secrets or passwords.

## Context engineering

The context window is the model's whole desk. **Context engineering** is the job of putting the right things on it. Four moves:

| Move | Meaning | Example |
|---|---|---|
| **Write** | save information outside the prompt | save a fact in the store, write notes to a file |
| **Select** | pick only what matters for this call | recall 3 facts, retrieve 4 chunks |
| **Compress** | make old text shorter | summarise the old chat, trim a long tool result |
| **Isolate** | give each sub-task its own small context | a sub-agent gets only its own task, not the whole chat |

Why bother? Three reasons:

1. **Cost and speed:** every token is billed and read.
2. **Quality:** the model forgets the middle of a long prompt (GenAI lesson 24) and can be distracted by noise.
3. **Safety:** less untrusted text in the prompt means less room for injection (lesson 15).

## Compress a long chat

Keep the last few messages word for word. Replace everything older with a short summary written by a model.

```python
# 8 messages, keep_last=3
# -> [summary_message, m5, m6, m7]
```

Rules that matter:

- If the chat is short, do nothing and make **no** model call.
- Summarise only the **older** part. The newest messages are the ones the user is asking about now.
- Tell the summariser to keep **names and decisions**. A summary that drops them is a silent bug.
- Put the summary in a system message with a clear label, so the model knows it is a summary and not a quote.

### Step by step: compress history (exercise 2)

1. If `len(messages) <= keep_last`, return the messages.
2. Split into `older` and `recent`. Handle `keep_last=0` on its own, since `messages[:-0]` is empty.
3. Make a transcript: one `role: content` line per older message.
4. Call the model once for a two-sentence summary.
5. Return `[summary_message] + recent`.

## Build the context with a budget

Put it all together. For each call build the message list in this order:

```
1. system prompt            (never dropped)
2. recalled facts           (selected, only if any matched)
3. recent history           (oldest dropped first when over budget)
4. the new question         (never dropped)
```

```python
while kept and size(messages + kept + tail) > max_chars:
    kept.pop(0)        # drop the oldest history message
```

A character budget is a rough stand-in for tokens (about 4 characters per token for English; GenAI lesson 2). For exact counts use the tokenizer of your model. In exercise 4 you write `build_context`.

## Try it live

1. Build a chat loop with `ChatGroq` or the Groq client. After each user message call `extract_facts`, and save the results with `save_fact`.
2. Quit the program. Start it again (save the dict to a JSON file first) and ask "what do you know about me?".
3. Print the context you send on each turn. Count the characters. Add `compress_history` when the history passes 2000 characters.
4. Try to break it: tell the bot a false fact, then correct it. What does your memory do? (A real system needs a way to update or remove a fact.)

## A little deeper

- **Memory writing in the background.** Extraction costs a model call. Many systems run it after the reply is sent, so the user does not wait.
- **Conflicts.** "I live in Pune" then "I moved to Delhi". Keep a date on each fact, and on conflict prefer the newer one, or ask the model to merge.
- **Forgetting.** Old, unused facts can expire. Memory that only grows turns into noise.
- **Scratchpad.** An agent can write notes to a file or state key during a long task and read them back later. This keeps long tasks from filling the window.
- **Prompt caching.** Many providers make a repeated prompt **prefix** cheaper (GenAI lesson 29). Keep the stable parts (system prompt, tool list) first and the changing parts last.
- **Trimming helpers.** LangChain has `trim_messages` to cut a message list by token count (name from memory; check the docs).

## Common mistakes

- Putting every fact into every prompt.
- Saving everything, including small talk.
- Trusting the extracted JSON without parsing and checking it.
- A summary that loses names and decisions.
- Summarising the **newest** messages and keeping the oldest.
- Dropping the system prompt or the user's question when over budget.
- Keeping memory forever, with no way for the user to see or delete it.
- Mixing users: one shared `store` key for everyone.

## Interview corner

**Short-term vs long-term memory in an agent?**
Short-term is the message state of one thread, saved by a checkpointer. Long-term is facts and events kept in a store across threads, recalled when relevant.

**How do you stop the context from growing forever?**
Keep recent messages, summarise older ones, select only relevant memories and chunks, trim long tool outputs, and set a token budget.

**What is context engineering?**
Choosing what goes into the context window: write (save outside), select (pick the relevant), compress (shorten), isolate (separate small contexts for sub-tasks).

**What are the risks of agent memory?**
Wrong facts that persist, privacy of personal data, memory poisoning (an attacker plants a fact through a tool result or a message), and growing noise. Validate what you save, let users delete it, and tag where each fact came from.

**Why does a longer context not always give better answers?**
The model uses the middle of a long prompt poorly, noise distracts it, and every token costs money and time.

## Summary

- The model has no memory. Short-term memory is the thread (checkpointer). Long-term memory is a per-user store.
- `save_fact` with de-duplication. `recall` picks only the matching facts (word match first, embeddings later).
- Let a model **extract** facts, then parse and validate the JSON. Bad output means save nothing.
- Context engineering has four moves: **write, select, compress, isolate**.
- Compress old chat into a summary. Keep recent messages word for word. Never drop the system prompt or the question.
- Treat memory as personal data: show it, delete it, and do not store secrets.
- Reference: `reference/agentic-langchain-langgraph.md`.
