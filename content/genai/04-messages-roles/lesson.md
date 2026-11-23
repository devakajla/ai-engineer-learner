---
title: Messages and roles
summary: Learn how a chat is sent to the model as a list of messages, what system, user and assistant roles do, why the model forgets everything between calls, and how to keep the history.
plan_ids: []
---

In lesson 3 you sent one message and got one answer. A real chat has many turns. In this lesson you learn how a whole conversation is sent to the model, and a surprising fact: the model does not remember anything by itself.

## The model has no memory

Imagine you call a helpful stranger on the phone. Each time you call, they pick up with **no memory** of earlier calls. If you want them to know what you said before, you must say it all again.

An LLM API works like this stranger. Every API call is a fresh start. The model does not remember your last call. Not one word.

So how does a chatbot "remember" what you said? **Your code sends the whole conversation again, every time.** The `messages` list is that conversation.

## What a message looks like

A **message** is one thing said in the chat. In Python it is a small dictionary with two keys:

- `role`: who is speaking.
- `content`: the text they said.

```python
message = {"role": "user", "content": "What is a variable?"}

message["role"]      # -> 'user'
message["content"]   # -> 'What is a variable?'
```

A conversation is a **list** of messages, in the order they were said:

```python
messages = [message1, message2, message3]
```

So `messages` is a list of dictionaries. You know both from Python level 1. Here they work together.

## The three roles

| Role | Who | What it is for |
| --- | --- | --- |
| `system` | You, the developer | Rules and personality. "You are a friendly tutor. Keep answers short." |
| `user` | The human | The question or request. |
| `assistant` | The model | The model's earlier replies. |

Here is a conversation as a list:

```python
messages = [
    {"role": "system", "content": "You are a helpful tutor. Answer in one sentence."},
    {"role": "user", "content": "What is a variable?"},
    {"role": "assistant", "content": "A name that points to a value."},
    {"role": "user", "content": "Give me an example."},
]
```

The model reads the list from top to bottom and writes the **next assistant message**. Because the earlier turns are in the list, it knows what "an example" refers to.

Remember lesson 1: the model continues text. The chat format is a clever way to say: "here is a conversation, continue it with the next assistant turn".

## The system message

The system message sets the rules for the whole chat. It goes **first**. In a normal app the user does not see it.

A good system message says:

- Who the model is ("You are a support agent for DevDocs").
- How to answer (short, polite, in English).
- What not to do ("If you do not know, say so").

```python
system = "You are a strict reviewer. Reply with one short sentence."
```

Keep it clear and short. Lesson 7 teaches how to write strong ones.

The system message is optional. If you do not need rules, leave it out.

## Building a messages list in code

You will build message lists in code all the time, so write a small function for it. Let's learn the pattern with a different example: a quiz.

### Step by step: a quiz question builder

We want `quiz_messages(topic)`. It returns a system message and a user message about the topic.

1. Make the system message dictionary.
2. Make the user message with an f-string, so the topic goes into the text.
3. Return both in a list, system first.

```python
def quiz_messages(topic):
    system = {"role": "system", "content": "You are a quiz master."}
    user = {"role": "user", "content": f"Ask me one question about {topic}."}
    return [system, user]

quiz_messages("Python")
# -> [{'role': 'system', 'content': 'You are a quiz master.'},
#     {'role': 'user', 'content': 'Ask me one question about Python.'}]
```

An **f-string** is a string that starts with `f`. Anything in `{ }` is replaced by its value.

The pattern: **build dictionaries, put them in a list, in the right order**. In the first exercise you use the same pattern, and also handle a missing system message.

## Growing the conversation

After each reply, add two things to the history: the user's question and the model's answer. The next call then sends the longer list.

```python
history = []

history = history + [{"role": "user", "content": "Hi"}]
history = history + [{"role": "assistant", "content": "Hello!"}]
len(history)   # -> 2
```

Look at `history + [new_item]`. It makes a **new list**. The other way, `history.append(item)`, **changes the list you already have**.

Making a new list is safer. If a function changes a list it was given, the code that called the function may be surprised by the change. A new list leaves the old one alone.

```python
old = [1, 2]
new = old + [3]
print(old)   # -> [1, 2]
print(new)   # -> [1, 2, 3]
```

A **turn** of chat does these steps:

1. Make the messages to send: the old history plus the new user message.
2. Call the model with them.
3. Take the reply text.
4. Return the reply **and** the new history (old, plus user, plus assistant).

```python
reply, history = chat_turn(client, history, "What is a list?")
reply, history = chat_turn(client, history, "And a tuple?")   # the model sees both turns
```

A function can return two values. Python packs them into a **tuple**. On the left side you **unpack** them into two names, as above.

In the third exercise you write `chat_turn`, using the function from the second exercise.

## Try it live

Prove that the model has no memory. Use your client from lesson 3:

```python
r1 = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "My name is Asha. Remember it."}],
)
r2 = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "What is my name?"}],
)
print(r2.choices[0].message.content)   # -> it does not know
```

Now send one list that holds the first question, the first answer and the second question. Ask again. This time it knows. The only difference is the list you sent.

## The cost of history

Each call sends **all** the old messages again. They count as input tokens (lesson 2). A long chat gets slower and costs more with every turn. In lesson 12 you learn to trim and summarise old messages.

A quick picture. If each turn adds about 100 tokens:

```
turn 1 sends   100 tokens
turn 2 sends   200 tokens
turn 3 sends   300 tokens
turn 10 sends 1000 tokens
```

All ten turns together send 5,500 tokens, not 1,000. The cost grows faster than the chat.

## A little deeper

- **The system message is not a safe lock.** A user can still try to talk the model out of its rules. Never put secrets in it. This is called prompt injection (lesson 7 and Level 5).
- **Order matters.** Models pay most attention to the system message and the most recent messages.
- **The model's "voice" is just text.** The `assistant` messages in your list do not have to be real. You can write fake ones to show the model an example of how to answer. This is called few-shot prompting (lesson 7).
- **Roles are a convention of the chat format.** Under the hood, the provider turns your list into one long text with special markers, and the model continues it.
- **More roles.** There is also a `tool` role for tool results (lesson 11).
- **Reasoning models** may also return their thinking text in a separate part of the reply. You do not send it back in the history. Lesson 34 shows how to handle it.

## Common mistakes

- Expecting the model to remember earlier calls without sending them.
- Putting the system message anywhere but first.
- Forgetting to add the model's reply to the history, so the next call looks like it never answered.
- Using `append` inside a helper and changing the caller's list.
- Storing the system message in the history and then sending it twice.

## Interview corner

**Is an LLM stateful?**
No. Each call is independent. The app stores the conversation and sends it again each time.

**What are the roles in the chat format?**
`system` (developer rules), `user` (the human), `assistant` (model replies). Later also `tool`.

**What is the system prompt for?**
To set the behaviour, tone and rules for the whole conversation, before any user message.

**Why does a long conversation get expensive?**
The full history is sent on every call, so input tokens grow with each turn. You trim or summarise old turns to control it.

## Summary

- The model has no memory. You send the whole conversation each call.
- A message is `{"role": ..., "content": ...}`. Roles: `system`, `user`, `assistant`.
- System message first. Then the turns in order.
- After a reply, add the user message and the assistant message to the history.
- Prefer `history + [item]` (a new list) over `.append` inside helpers.
- Project: step 2 adds a system prompt and a `chat_turn` function to DevDocs Copilot.
- Reference: `reference/genai-groq.md`.
