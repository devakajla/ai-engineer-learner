---
title: "Choosing a model: open vs closed, size, speed and cost"
summary: Learn how to pick the right model for a task, what open and closed models are, how size, speed and price trade off, and how to fall back when a model fails.
plan_ids: []
---

By now you know what an LLM is, what a token is, and how to call one. A real question comes next: **which model should I call?**

There are hundreds. Picking the biggest one every time is a mistake. It costs more and is slower. Picking the smallest one every time is also a mistake. It may fail at the task. A good AI Engineer picks on purpose, and can explain why. Interviewers love this question.

## What changes from model to model

Models differ in five ways:

| Thing | What it means | Why you care |
| --- | --- | --- |
| **Quality** | How good the answers are | Wrong answers cost you users |
| **Speed** | Time to first token, and tokens per second | Slow apps feel broken |
| **Price** | Cost per million input and output tokens | Money, at scale |
| **Context window** | How many tokens fit (lesson 2) | Long documents need big windows |
| **Features** | Tool calling, JSON output, images, reasoning | Some tasks need them |

You never get all of the best at once. A big model is smart but slow and costly. A small model is fast and cheap but makes more mistakes. You pick the best **balance for the task**.

## Size: 8B, 70B and so on

You saw "8B" and "70B" in model names. That is the number of dials (parameters), in billions.

- **Small (about 1B to 10B)**: fast, cheap. Good for easy jobs: classify text, pull out fields, short rewrites.
- **Medium and large (30B to 100B+)**: slower, costlier, smarter. Good for harder jobs: long reasoning, tricky code, careful writing.

A simple rule: **start with a small model. Move up only if it fails on your own test examples.**

## Open models and closed models

**Closed models** (for example GPT, Claude, Gemini) can only be used through the owner's API. You cannot download them.

**Open models** (for example Llama, Qwen, Mistral) have downloadable weights. Anyone can run them. Some open models still have licence rules, so read the licence.

| | Open | Closed |
| --- | --- | --- |
| Where it runs | Your computers, or a host like Groq | The owner's servers |
| Data privacy | You can keep data inside your own network | Data goes to the provider |
| Cost shape | You pay for computers, or per token at a host | You pay per token |
| Quality at the top | Close, sometimes behind | Often the best |
| Control | You can fine-tune and change a lot | Limited |

Groq is a host. It runs **open** models on its own fast chips and sells them per token. So one API call gives you an open model at high speed.

> Model names and prices change often. Always check `console.groq.com/docs/models` for what exists now. Do not copy old tables from the internet.

## Speed has two numbers

1. **Time to first token (TTFT)**: how long before the first word appears. It matters for chat.
2. **Tokens per second**: how fast the rest appears. It matters for long answers.

Bigger models are slower on both. Streaming (lesson 6) hides some of the wait.

## How to choose: a simple method

1. **Write down the task**, and what "good" means. ("Extract a date from an email. Must be right 95 times in 100.")
2. **Collect 20 to 50 real examples** with the right answers.
3. **Try the smallest model.** Count how many it gets right.
4. If it is not good enough, **try the next size up.**
5. **Compare cost and speed** at your real traffic.
6. **Re-check later.** New models arrive all the time.

Public leaderboards and benchmarks help you shortlist. They do not replace your own examples, because your task is not their task.

## Worked example: cheapest that fits

A common job: among the models that can do the work, pick the **cheapest**. Let's practise the pattern with a different example: phone plans. Each plan has a price and a data amount in GB. You need at least 20 GB. Which is the cheapest plan with enough data?

1. Start with nothing chosen: `best_name = None`, `best_price = None`.
2. Go through each plan.
3. **Skip** plans that do not have enough data.
4. If nothing is chosen yet, or this plan is cheaper, choose it.
5. Return the chosen name.

```python
plans = {
    "basic": {"price": 10, "gb": 5},
    "plus": {"price": 18, "gb": 25},
    "max": {"price": 30, "gb": 100},
}

best_name = None
best_price = None
for name, plan in plans.items():
    if plan["gb"] < 20:
        continue                      # not enough data, skip
    if best_price is None or plan["price"] < best_price:
        best_name = name
        best_price = plan["price"]

print(best_name)   # -> plus
```

`continue` jumps to the next item in the loop. The pattern is: **filter, then find the best**. You will use it in the second exercise.

## Fallback: when a model fails

Sometimes a model is down, busy, or rate limited (lesson 6). A **fallback** is a plan B: try another model.

The idea in steps:

1. Have a list of models, best first.
2. Try the first. If it works, return its answer.
3. If it raises an error, remember the error and try the next.
4. If all fail, raise the last error.

```python
def first_that_works(actions):
    last_error = None
    for action in actions:
        try:
            return action()
        except Exception as e:
            last_error = e
    raise last_error
```

(The `action()` call is a small trick. Here each item is a function we call. In your exercise, you will loop over model names instead.)

You will use this pattern in the third exercise. It keeps your app up, at lower quality, when the best model is not available.

## Routing: use the right model for each job

Many apps use **more than one** model:

- A small, fast model for simple steps (classify the question, extract fields).
- A big model for the hard step (write the final answer).

Choosing the model per request is called **routing**. It often cuts cost a lot, with almost the same quality.

## Try it live

Use the same prompt on two Groq models (a small and a large one) in the Playground, or in code with the `ask` function from lesson 3. Compare:

1. Is the answer different? Is the big one clearly better?
2. How long did each take?
3. Look at `response.usage` and work out the cost of each with `estimate_cost` from lesson 2.

## A little deeper

- **Benchmarks lie a little.** Models may have seen benchmark questions during training. Use your own examples.
- **Quantised models.** A model can be shrunk (stored with fewer bits per number). It runs cheaper and faster, with a small loss in quality.
- **Latency budget.** If your app must answer in 2 seconds, that limit chooses the model, not quality alone.
- **Vendor lock-in.** Keep provider code in one place (lesson 3). Many providers copy the same API shape, so switching is easy if you keep it tidy.
- **Rate limits differ by model.** A small model often has higher limits.
- **Specialised models.** There are models for code, for images, for speech and for embeddings. A general chat model is not always the best choice.

## Common mistakes

- Always using the biggest model.
- Choosing by a leaderboard without testing on your own examples.
- Forgetting that output tokens cost more than input tokens.
- No fallback, so one outage stops the whole app.
- Hard-coding model names all over the code, which makes changes painful.

## Interview corner

**How do you choose a model for a task?**
Define what good means, collect real examples, start with the smallest model, move up only if it fails, and compare quality, latency and cost.

**Open vs closed models: what are the trade-offs?**
Open models give control, privacy and lower cost at scale, but you must host them or use a host. Closed models are often the strongest and easiest, but data goes to the provider and you have less control.

**What is model routing?**
Sending each request to the model that suits it: a small model for easy steps, a big model for hard ones. It lowers cost and latency.

**What is a fallback and when do you need one?**
A backup model used when the main one fails or is rate limited. You need it in any app that must stay up.

## Summary

- Models differ in quality, speed, price, context size and features. You cannot maximise all of them.
- Start small. Move up only when your own test examples fail.
- Open models have downloadable weights. Closed models are API-only. Groq hosts open models.
- Pick "cheapest that fits" with a filter-then-best loop.
- A fallback tries the next model when one fails. Routing sends each task to the right model.
- Always check the current model list and prices on `console.groq.com/docs/models`.
