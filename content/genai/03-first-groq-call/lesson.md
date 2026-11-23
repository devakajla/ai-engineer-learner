---
title: Setup and your first Groq call
summary: Get a Groq API key, keep it safe, install the SDK, make your first model call, read the reply and its token counts, and wrap it in a function.
plan_ids: []
---

Time to call a real model from Python. In lessons 1 and 2 you learned what a model is. Now you will talk to one.

We use **Groq**. It runs open models (like Llama) very fast, and its API is simple. You will need an account and a key. This lesson walks you through every step.

## What is an API?

Think of a restaurant. You do not walk into the kitchen. You tell the waiter what you want. The waiter takes it to the kitchen and brings the food back.

An **API** is the waiter between two programs. Your Python program sends a **request**. Another program, on a computer far away, does the work and sends back a **response**.

For an LLM:

```
Your Python code  --request (your text)-->  Groq's computers (the model runs here)
Your Python code  <--response (the answer)--  Groq's computers
```

The model does not run on your laptop. It runs on Groq's computers. That is why you need the internet, and why you need to prove who you are.

## What is an SDK?

Sending a request by hand is fiddly. An **SDK** (software development kit) is a ready-made Python package that does the fiddly part. You write normal Python lines. The SDK builds the request, sends it, and gives the answer back as Python objects.

Groq's SDK is called `groq`.

## Step 1: Get an API key

An **API key** is like a password for your program. It tells Groq "this request is from me". Groq uses it to know whose limits and bill to use.

1. Go to `console.groq.com` and sign in.
2. Open **API Keys** and create a key. It starts with `gsk_`.
3. Copy it right away. You cannot see it again later.

> Groq has had a free plan with limits. Plans and limits change, so check the console for the current rules.

## Step 2: Keep the key out of your code

Never write a key inside your code. If you push that code to GitHub, anyone can see it and use your key (and your money).

Instead, put it in an **environment variable**. This is a named value that lives in your terminal, outside your files. Your programs can read it by name.

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

This works only in the current terminal window. To keep it, add the same line to your shell settings file (for example `~/.zshrc`).

In Python, read it with the `os` module:

```python
import os

key = os.environ.get("GROQ_API_KEY")
print(key is None)   # -> False if you set it, True if you forgot
```

`os.environ` works like a dictionary of all environment variables. Reading `os.environ["GROQ_API_KEY"]` stops with a `KeyError` if the key is missing. `.get("GROQ_API_KEY")` gives `None` instead. You will write a safe reader in the second exercise.

## Step 3: Install the SDK

```bash
uv add groq
```

(Without `uv`, use `pip install groq`.) This downloads the `groq` package so you can `import` it.

## Step 4: The first call

```python
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "Say hello in one short sentence."}],
)

print(response.choices[0].message.content)
# -> Hello! It's nice to meet you.
```

Your answer will use different words. Models do not always give the same words. That is normal.

Let's read it line by line.

- `from groq import Groq` brings in the tool we need.
- `Groq(api_key=...)` makes a **client**. A client is an object that holds your key and knows how to talk to Groq. You make it once.
- `client.chat.completions.create(...)` sends the request. Read the dots left to right: the client, its chat part, its completions part, and then the action `create`. "Completion" is the word for "the model completes the text".
- `model` says which model to use. `qwen/qwen3.8-27b` is the default model for this whole track. It is a mid-size model (27B means 27 billion dials). `llama-3.1-8b-instant` is smaller and faster. `llama-3.3-70b-versatile` is bigger. Names change, so check `console.groq.com/docs/models`.
- `messages` is a list of messages. Each message is a dictionary with a `role` (who speaks) and `content` (the text). Here there is one message, from the `user`. Lesson 4 explains roles.

## Reading the reply

`response` is an object with parts. You read a part with a dot, like `response.model`.

```python
response.choices[0].message.content    # the text of the answer
response.choices[0].finish_reason      # why it stopped: 'stop' or 'length'
response.usage.prompt_tokens           # input tokens used
response.usage.completion_tokens       # output tokens used
response.usage.total_tokens            # both added
```

Why `choices[0]`? The API can return several answers to one question. `choices` is a **list** of them. You normally ask for one, so you take the first item: `[0]`. (Lists start counting at 0.)

`finish_reason` is `'stop'` when the model finished by itself. It is `'length'` when it ran out of its answer limit and was cut off (lesson 5).

`usage` gives the real token counts from lesson 2. This is how you work out the real cost of a call.

## Try it live

Run the first call yourself. Then print `response.usage`. Change the question to a much longer one and see how `prompt_tokens` grows. Compare it with your `estimate_tokens` guess from lesson 2. How close were you?

If you see an error, read the last line. The usual ones: `AuthenticationError` (wrong or missing key), `NotFoundError` (wrong model name).

## Put it in a function

Do not scatter API calls all over your code. Write one small function. Give it the **client** as an argument:

```python
def ask(client, question):
    ...
```

Why pass the client in? Because your tests can then pass a **fake client**. A fake client is an object that looks like the real one but does not use the internet. Tests run fast and need no key. The exercises in this track do exactly that.

### Step by step: a `summarize` function

Let's write a function that asks for a one-sentence summary of some text.

1. Build the prompt: an instruction plus the text.
2. Put it in a messages list, as one user message.
3. Call `client.chat.completions.create(...)` with a model and the messages.
4. Take the text from `response.choices[0].message.content`.
5. Return it.

```python
def summarize(client, text):
    prompt = "Summarize this in one sentence:\n" + text
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
    )
    return response.choices[0].message.content

# summarize(client, "Python is a language. It is easy to read.")
# -> 'Python is an easy-to-read programming language.'
```

The pattern is always the same: **build messages, call, return the text**. You will use it in the first exercise.

## A little deeper

- **What really happens.** The SDK sends an HTTPS `POST` request to `https://api.groq.com/openai/v1/chat/completions`, with your key in a header and your messages as JSON (a text format for data, which looks like a Python dictionary). You could do the same with `curl` or `httpx`. The SDK adds convenience.
- **OpenAI-compatible.** Groq copied the OpenAI API shape. Code like this often works with other providers if you change the key, the URL and the model name. That is a good reason to keep your API code in one small place.
- **Auto retry.** The SDK retries some failures by itself. You will control that in lesson 6.
- **Reuse the client.** Make the client once and reuse it. Do not make a new one for every call.
- **Async.** There is also `AsyncGroq`, which works with `await`. You will use it when serving many users at once.

## Common mistakes

- Writing the key in the code, or committing a `.env` file to git.
- Printing the whole `response` and then searching for the text. The text is in `response.choices[0].message.content`.
- Forgetting `[0]` after `choices`.
- Using a model name that no longer exists. You get a "model not found" error. Check the models page.
- Setting the key in one terminal window and running the code in another.

## Interview corner

**How do you keep API keys safe?**
Use environment variables or a secrets manager. Never commit keys. Add `.env` to `.gitignore`. Use a separate key for each app so you can switch one off.

**Why pass the client into your function instead of creating it inside?**
It is easier to test, because you can pass a fake. It also lets you reuse one client and swap providers later.

**What does `finish_reason` tell you?**
Why the model stopped. `stop` means it ended naturally. `length` means it hit the token limit and the answer is cut off.

**What does the `usage` field give you?**
Input, output and total token counts for the call. You use it to track cost.

## Summary

- An API is a way for programs to talk. Your code sends a request, the model's computers send a response.
- An API key is a secret. Keep it in an environment variable, not in code.
- `uv add groq`, then `Groq(api_key=...)`.
- `client.chat.completions.create(model=..., messages=[...])` makes the call.
- The text is `response.choices[0].message.content`. Token counts are in `response.usage`.
- Write functions that take a `client`, so tests can pass a fake.
- Project: this lesson starts **DevDocs Copilot**. Open the Project tab.
- Reference: `reference/genai-groq.md`.
