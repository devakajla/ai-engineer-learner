# 9. Chat memory and long conversations

Chapter 3 said the model has no memory: you resend the history every time. That is simple until the history gets **long**. Then it costs too much, runs slow, and finally does not fit in the context window. This chapter covers how to decide what to keep.

## What "memory" really is

@@ grid 2 | Figure 9.1: two kinds of memory.
Short-term|the messages you send in this request;lives in the context window|blue
Long-term|facts saved outside the model;in a database, loaded when needed|green
@@ end

The model's "memory" is only whatever you put in the prompt. So **memory design is prompt design**: what to include, what to drop, what to summarise.

## Strategy 1: keep everything (and its limit)

Appending every turn is correct for short chats. The problem is growth: turn 50 sends 49 earlier turns again. Cost grows with every turn, and finally you hit the window. So you need a policy.

## Strategy 2: a sliding window

Keep the **system message** and only the **most recent** messages that fit in a budget. Drop the oldest first.

```python
def trim(messages, budget, count):
    system = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]
    used = sum(count(m) for m in system)
    kept = []
    for message in reversed(rest):        # newest first
        cost = count(message)
        if used + cost > budget:
            break
        kept.append(message)
        used += cost
    return system + kept[::-1]            # restore the normal order
```

Why it works, step by step: the system message is always kept, since the rules must never fall out. Then we walk the rest from the **newest** to the oldest, adding messages while the budget allows, and stop at the first one that does not fit. We reverse the list at the end so the order is natural again.

Tested with ten short messages and a budget of 50 tokens (each message about 11 tokens), it kept the system message plus the **three newest**. `count` can use `tiktoken` (chapter 2): `len(enc.encode(m["content"])) + 4`, where the `+ 4` is a rough allowance for the message's formatting.

The weakness: the model completely **forgets** old facts, such as the user's name, however important.

## Strategy 3: summaries

Instead of dropping old messages, **replace them with a short summary** written by the model itself.

```python
def summarise(client, old_messages):
    text = "\n".join(f"{m['role']}: {m['content']}" for m in old_messages)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Summarise this conversation in under 80 words. Keep names, numbers, decisions and open questions."},
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_completion_tokens=150,
    )
    return response.choices[0].message.content
```

Then the history sent to the model becomes:

```
[system rules]
[system: "Summary of earlier chat: ..."]
[the last few real messages]
```

@@ flow | Figure 9.2: summary memory.
Old messages|turns 1 to 20|gray -> Summary|80 words;made by the model|yellow -> New prompt|rules + summary;+ last few turns|green
@@ end

A common rule: when the history passes N tokens, summarise everything except the last K messages, and keep the summary for next time. The cost is one extra call now and then. The risk: a summary can **lose or distort** details, so tell it exactly what to keep.

## Strategy 4: long-term memory (facts)

Some things should survive across chats and days: the user's name, language, preferences. Store them **outside** the prompt, for example in a database table, and add the relevant ones to the system message when the chat starts:

```python
def build_system(base_rules, user_facts):
    facts = "\n".join(f"- {k}: {v}" for k, v in user_facts.items())
    return f"{base_rules}\n\nKnown facts about the user:\n{facts}"

print(build_system("Be brief.", {"name": "Dev", "goal": "AI engineer"}))
# -> Be brief.
# ->
# -> Known facts about the user:
# -> - name: Dev
# -> - goal: AI engineer
```

How do facts get into the store? Either the app saves them from explicit forms, or a small extra model call looks at each turn and **extracts** facts worth remembering (using structured output, chapter 7). For large amounts of memory (thousands of notes), store them as **embeddings** and retrieve only the relevant ones, the same idea as RAG (chapter 10 onward).

## What is a good policy?

| Situation | Use |
| --- | --- |
| short chat, 10 or fewer turns | keep everything |
| long chat, only recent context matters | sliding window |
| long chat, early facts matter | summary plus recent messages |
| a user returns on another day | long-term facts in a store |
| huge history, search needed | embeddings and retrieval |

## Practical details

- **Per-user storage.** Keep a history per conversation id, in a database or Redis. Never mix users.
- **Privacy.** Histories hold personal data. Decide how long to keep them and who can read them.
- **Cost view.** Count total tokens sent per turn and log them. Watching this number rise tells you when you need a policy.
- **Do not trim the middle blindly.** A tool call message must stay with its tool result. A trim that separates them breaks the request.

::: {.box .checkpoint}
**Checkpoint:** you can explain the difference between a sliding window and a summary, and name one thing each loses.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Letting the history grow with no limit until the request fails.
- Trimming away the system message.
- Splitting a tool call from its result when trimming.
- A summary that is too vague and loses key facts.
- Sharing one history between different users.
- Storing personal data forever without a reason.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you give a chatbot memory?** Store the messages and resend the relevant ones each turn. Use a sliding window or summaries when the history is long, and a database or vector store for long-term facts.

**Q: Sliding window vs summary memory?** A window keeps recent messages exactly but forgets older ones. A summary compresses older content but can lose detail.

**Q: Why does cost rise with chat length?** The whole history is input tokens on every request.

**Q: What is long-term memory in an LLM app?** Facts stored outside the model and inserted into the prompt when relevant.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `trim` with a word-based `count` and test it on 10 messages.
2. Make `trim` never drop the first user message, even when over budget. What trade-off does that create?
3. Write `maybe_summarise(client, messages, limit)` that summarises when the history is longer than `limit` messages and keeps the last four. Test it with a fake client.
4. Build the system message from a facts dictionary, and test that an empty dict adds no "Known facts" section.
5. **Think:** why is it risky to keep the entire chat history of every user for years?
:::
