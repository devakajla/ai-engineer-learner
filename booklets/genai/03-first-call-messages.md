# 3. Your first API call: messages and roles

Time to talk to a model from code. We use **Groq**, which serves open models very fast and has a free tier. The ideas are the same for OpenAI, Anthropic and others. Only small details differ.

> **Honesty note.** The Groq calls in this booklet were not run here, because no API key was used. Names of functions, parameters and errors were checked against the installed SDK (`groq` 1.7). Model names change often. Check `console.groq.com/docs/models` for the current ones before you copy any.

## Setup

1. Make a free account at `console.groq.com` and create an **API key**.
2. Save it as an **environment variable**, never inside your code or git:

```bash
export GROQ_API_KEY="gsk_...your key..."
```

3. Install the SDK in your project: `uv add groq`.

Why an environment variable? Code gets copied, pushed to GitHub and shared. A key in code leaks. A variable stays on your machine. (For projects, put it in a `.env` file that is in `.gitignore`.)

## The first call

```python
from groq import Groq

client = Groq()   # reads GROQ_API_KEY from the environment

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain a token in one sentence."}],
    max_completion_tokens=100,
)

print(response.choices[0].message.content)
# -> A token is a small piece of text, often part of a word, that a language model reads and writes.
```

(The exact words will differ every time.) Let us go through each part:

- `Groq()` makes a **client**: the object that holds your key and talks to the server. Make **one** and reuse it.
- `client.chat.completions.create(...)` sends one request and waits for the full answer.
- `model` chooses which model answers. Smaller means faster and cheaper, larger means smarter.
- `messages` is the **conversation so far** (explained below).
- `max_completion_tokens` caps the length of the answer, so cost and time stay limited. (An older name, `max_tokens`, is being retired.)

## What the response holds

`response` is an object with several fields. These matter:

| Field | What it is |
| --- | --- |
| `choices[0].message.content` | the answer text |
| `choices[0].finish_reason` | why it stopped: `"stop"` (finished) or `"length"` (hit the token limit, answer is cut off) |
| `usage.prompt_tokens` | tokens you sent |
| `usage.completion_tokens` | tokens it wrote |
| `usage.total_tokens` | the sum, which is what you pay for |

Always look at `finish_reason`. If it says `"length"`, the answer was cut mid-sentence, and you may need a larger limit.

`usage` is your meter. Log it on every call, and you can always compute your cost (chapter 2).

## Messages and roles

The model does not receive a single string. It receives a **list of messages**, and each message has a **role** and some **content**.

| Role | Who speaks | Use |
| --- | --- | --- |
| `system` | you, the developer | rules and behaviour: "You are a polite support agent. Answer in two sentences." |
| `user` | the person | the question or task |
| `assistant` | the model | an earlier reply (so the model sees the history) |
| `tool` | your code | the result of a tool the model asked for (chapter 8) |

```python
messages = [
    {"role": "system", "content": "You are a pirate. Keep answers to one sentence."},
    {"role": "user", "content": "What is Python?"},
]
```

The **system message** is the strongest way to set tone, format and limits. Put the instructions that must always hold there, not in the user's message.

## The model has no memory

This is the idea that surprises everyone. The API is **stateless**: each request is independent. The model remembers *nothing* from the previous call. A chat feels continuous only because **you resend the whole conversation each time**.

```python
messages = [{"role": "user", "content": "My name is Dev."}]
reply = client.chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=50)

messages.append({"role": "assistant", "content": reply.choices[0].message.content})
messages.append({"role": "user", "content": "What is my name?"})
reply2 = client.chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=50)
# the model answers "Dev" only because the first exchange is inside `messages`
```

If you leave the history out, the model has no way to know your name. Consequences:

- Your app must **store** the history (a list, or a database).
- Each turn **costs more**, since the history is sent again.
- The history can outgrow the window, so you must shorten it (chapter 9).

@@ flow | Figure 3.1: a chat is the same list, growing with every turn.
Turn 1|[user]|blue -> Turn 2|[user, assistant, user]|green -> Turn 3|[user, assistant, user, assistant, user]|yellow
@@ end

## A small helper you will reuse

Wrapping the call in a function keeps your code tidy, and **accepting the client as an argument** makes it testable.

```python
def ask(client, question, system="You are a helpful assistant.", model="llama-3.1-8b-instant"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        max_completion_tokens=300,
    )
    return response.choices[0].message.content
```

Why pass `client` in? In a test you do not want a real call (slow, costs money, different every time). You pass a **fake** that returns fixed text. This offline run works without any key:

```python
import types

class FakeClient:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        message = types.SimpleNamespace(content=self.reply)
        choice = types.SimpleNamespace(message=message, finish_reason="stop")
        return types.SimpleNamespace(choices=[choice])

fake = FakeClient("Hi!")
print(ask(fake, "hello"))
# -> Hi!
print(fake.calls[0]["max_completion_tokens"])
# -> 300
```

The fake copies only the shape of the real object (`.chat.completions.create(...)` returning `.choices[0].message.content`). It also **records** the arguments, so a test can check that we really sent the token limit. You will see this pattern throughout the booklet.

## Reading and handling a failure

A call can fail. Wrap it, and catch the SDK's errors:

```python
import groq

try:
    text = ask(client, "Hello")
except groq.AuthenticationError:
    print("Bad API key")
except groq.RateLimitError:
    print("Too many requests, slow down")
except groq.APIConnectionError:
    print("Network problem")
```

Chapter 5 turns this into a proper retry strategy.

::: {.box .checkpoint}
**Checkpoint:** a call returns text, you print `usage.total_tokens`, and you can explain why the second question in a chat only works if you resend the first exchange.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Putting the API key in code or committing `.env`.
- Believing the model remembers earlier calls.
- Putting permanent rules in the user message instead of `system`.
- Ignoring `finish_reason == "length"`, so truncated answers go unnoticed.
- Creating a new client for every request.
- Calling the real API in tests.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Are LLM APIs stateful?** No. Every request is independent, so the client resends the conversation history each time.

**Q: What are the message roles?** `system` for developer instructions, `user` for the person, `assistant` for model replies, `tool` for tool results.

**Q: What does `finish_reason: "length"` mean?** The output hit the token limit and is cut off.

**Q: Why not hard-code an API key?** It leaks through git and logs. Use environment variables or a secret manager.

**Q: How do you test code that calls an LLM?** Inject the client and pass a fake in tests.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make a call with a `system` message that forces one-word answers. Try three questions.
2. Print `usage.prompt_tokens` and `usage.completion_tokens`, and compute the cost with prices from the Groq page.
3. Set `max_completion_tokens=5` and look at `finish_reason`. What do you get?
4. Write `chat(client, history, user_text)` that appends the user message, calls the model, appends the reply, and returns the reply.
5. Test `chat` with a fake client and check that the second call sent both earlier messages.
6. **Think:** why does a long conversation get more expensive with each turn?
:::
