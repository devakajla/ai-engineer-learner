---
title: "Level 1 project: build your own llm.py"
summary: Put every Level 1 piece together into one small, careful LLM client - chat with history, settings, retries, cost and safety checks - and review the Level 1 ideas as interviewers ask them.
plan_ids: []
---

You now know the parts: tokens and cost, messages and roles, settings, model choice, streaming, errors and retries, and thinking output. Each part was a small function.

In real work, these parts live together in one small file. In this project you build it: `llm.py`. It is the toolbox for every later level.

Why do this? Because a good AI Engineer does not call `client.chat.completions.create(...)` in fifty places. They wrap it once, carefully, and reuse the wrapper. That wrapper holds the settings, the retries, the cost tracking and the safety checks in one place.

## The pieces you already have

Every piece below came from a lesson. In the exercises of this lesson they are **given** to you, so you can focus on putting them together.

| Piece | From lesson | What it does |
| --- | --- | --- |
| `estimate_tokens`, `fits` | 2 | Guess the size of a prompt. Check it fits the window |
| `estimate_cost` | 2 | Cost from token counts and prices |
| `build_messages`, `add_turn` | 4 | Build the messages list and grow the history |
| `build_params` | 5 | The settings for a task (`extract`, `chat`, `creative`) |
| `usage_summary` | 3 | Read the token counts from a response |
| `backoff_delays` | 6 | The waits between retries |

The new skill is **composing**: using small, tested functions to build a bigger one. If each piece is correct, the big one is easier to get right.

## A worked example of composing

Let's build a small tool with the same idea, using different pieces: a shopping total with tax and a discount.

Given pieces:

```python
def add_tax(price, rate):
    return round(price * (1 + rate), 2)

def apply_discount(price, percent):
    return round(price * (1 - percent / 100), 2)
```

We want `final_price(price, percent, rate)`: discount first, then tax. Steps:

1. Apply the discount to the price.
2. Add tax to the result.
3. Return it.

```python
def final_price(price, percent, rate):
    discounted = apply_discount(price, percent)
    return add_tax(discounted, rate)

final_price(100, 10, 0.2)   # -> 108.0
```

Notice what we did **not** do: we did not repeat the maths. We called the pieces in the right order. Your `chat` function in the first exercise is the same: it calls the pieces in the right order.

## The three tools you build

**1. `chat`**: one turn of a chat, with the settings for a task, the history, and retries with waits. It combines lessons 4, 5 and 6.

**2. `call_cost`**: reads a response and returns the usage, the cost, and whether the answer was cut off (`finish_reason == "length"`). It combines lessons 2, 3 and 5.

**3. `safe_ask`**: checks that the prompt **fits** the window **before** calling, makes the call with the right settings, and returns the answer with its cost. It combines lessons 2, 3, 4 and 5.

After this lesson you have a small library that you can reuse in every project of this track.

## Try it live

Copy the given pieces and your three finished functions into one file `llm.py`. Then run:

```python
import os
from groq import Groq
from llm import chat

client = Groq(api_key=os.environ["GROQ_API_KEY"])
reply, history = chat(client, [], "Explain a token in one sentence.", task="chat")
reply, history = chat(client, history, "Now explain it to a child.", task="chat")
print(reply)
```

Pass `sleep=time.sleep` to wait between retries. Turn your key off on purpose and watch the error. Then check `call_cost` on a real response and compare the cost with the price page of the provider.

## A little deeper

- **Dependency injection.** You pass the `client` and the `sleep` function into your functions instead of creating them inside. This is what makes them easy to test. The name for the idea is *dependency injection*.
- **One place for model names.** Keep the model name in one constant, not in fifty strings. Changing the model then takes one edit.
- **Logging.** In a real wrapper, you also log the model, the token counts, the time taken and the cost of every call. You will add this in Level 5.
- **Which errors to retry.** Our `chat` retries any error, to keep the exercise simple. In real code, retry only the retryable ones from lesson 6.
- **Async.** Real servers use an async client so one process can wait for many calls at once. The idea stays the same.

## Common mistakes

- Calling the API directly all over the code, so settings and retries are copied and drift apart.
- Changing the history list the caller passed in.
- Checking the size after the call, not before.
- Waiting after the last failed try, which wastes time.
- Not checking `finish_reason`, so cut-off answers look complete.

## Interview corner

These are Level 1 questions in the way interviewers ask them. Say the answer out loud first.

**What is an LLM, and what does it do at each step?**
A large neural network that predicts the next token from the tokens before it. Repeating that step gives a full answer.

**How would you make a chat remember things?**
The model is stateless. Store the history in your app and send it with every call. Trim or summarise it when it grows.

**A call returns an answer that stops in the middle of a sentence. Why?**
It hit `max_completion_tokens`. `finish_reason` is `length`. Raise the limit, ask for a shorter answer, or handle it in code.

**How do you make an LLM call reliable?**
Set a timeout, retry only retryable errors with exponential backoff and jitter, add a fallback model, and check the output.

**How do you pick a model and control cost?**
Start with a small model, test on your own examples, move up only if needed, cap the output, and track `usage` per call.

## Summary

- Small tested pieces, composed in the right order, make a reliable client.
- `chat`: history + task settings + retries with backoff.
- `call_cost`: usage, cost and a cut-off flag from one response.
- `safe_ask`: check the size first, then call, then report the cost.
- Pass the client and `sleep` in, so the code is easy to test.
- This `llm.py` is your base for Levels 2 to 5.
