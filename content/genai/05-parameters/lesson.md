---
title: "Parameters: temperature, token limits and more"
summary: Learn the settings that change how a model answers (temperature, max_completion_tokens, top_p, top_k, stop, seed) and how to choose and check them.
plan_ids: []
---

So far you sent a model name and some messages. The `create` call has more settings that change **how** the model answers. In this lesson you learn the ones you will use all the time.

A **parameter** is just a setting you pass to the call. Think of the dials on an oven: temperature, timer. The oven is the same, but the dials change the result.

## First, the idea: the model draws from a list of chances

Remember lesson 1: at each step the model gives a chance to every possible next word. For example, after "The sky is", the chances might be:

```python
chances = {"blue": 0.6, "clear": 0.2, "grey": 0.15, "falling": 0.05}
```

The model **draws one** word from this list. It does not always pick the top one. It is like rolling a loaded dice where "blue" is likely and "falling" is rare.

The settings in this lesson change **how** the model draws. Some make it pick the safest word. Some let it take more risk.

## `temperature`: how adventurous

**Temperature** is the main dial.

- **Low** (0 to 0.3): it almost always picks the most likely word. Answers are steady, focused and repeatable.
- **High** (0.8 and up): it sometimes picks less likely words. Answers are more varied and creative, and also more likely to go wrong.

On Groq the value goes from `0` to `2`.

| Task | Good temperature |
| --- | --- |
| Pull data out of text, classify, write code | `0` to `0.3` |
| Normal chat and answers | `0.5` to `0.8` |
| Stories, names, brainstorming | `0.9` to `1.2` |

For DevDocs Copilot, you want facts from the docs, so use a low value.

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    temperature=0,
)
```

## `max_completion_tokens`: a limit on the answer

This is the **most tokens the answer can have**. (Tokens are about 4 characters, lesson 2.)

Why use it?

- It stops a rambling answer from costing too much.
- It keeps answers short for a small screen.

If the model hits the limit, it **stops in the middle of a sentence**, and `finish_reason` is `"length"` (lesson 3). A cut-off answer is not an error. The call succeeds. You must check for it yourself.

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    max_completion_tokens=100,
)
```

> Older code uses the name `max_tokens`. Groq's SDK still accepts it, but marks it as deprecated. Use `max_completion_tokens` in new code.

## `top_k` and `top_p`: cut the list short

Another way to control the draw is to **remove the unlikely words first**.

- **`top_k`** keeps only the `k` most likely words. With `top_k=2`, only "blue" and "clear" stay in the draw.
- **`top_p`** keeps the best words until their chances add up to `p`. With `top_p=0.8`, "blue" (0.6) and "clear" (0.2) add up to 0.8, so only those two stay.

Both stop the model from drawing a very strange word like "falling".

Here is `top_k` in plain Python (a sketch, ties aside):

```python
pairs = []
for word, chance in chances.items():
    pairs.append((chance, word))
best_two = sorted(pairs, reverse=True)[:2]
print(best_two)   # -> [(0.6, 'blue'), (0.2, 'clear')]
```

`sorted(..., reverse=True)` puts the biggest first. `[:2]` keeps the first two.

> Groq's chat API supports `top_p` but, at the time of writing, not `top_k`. Some other providers and local models offer both. Check the docs of the provider you use.

With `top_p=0.1` the model is very focused. With `top_p=1` it considers every word.

The advice from the docs: change **temperature or top_p, not both**. For most work, just use temperature.

## `stop`: where to end

`stop` is a text (or a list of texts). The model stops writing as soon as it would write one of them. The stop text itself is not in the answer.

```python
stop=["\n\n"]    # stop at the first blank line
stop="END"       # stop at the word END
```

This helps when you ask for a list or a single line and do not want extra talk.

## `seed`: try to repeat an answer

`seed` is a number. With the same seed and the same settings, the model *tries* to give the same answer. It is **best effort**, not a promise. It helps when you debug.

```python
seed=42
```

## Sending settings from a dictionary

When you have many settings, keep them in a dictionary. Then spread it into the call with `**`:

```python
params = {"temperature": 0, "max_completion_tokens": 200}

response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    **params,
)
```

`**params` means "take every key and value of this dictionary and pass them as named arguments". It is the same as writing `temperature=0, max_completion_tokens=200`.

## Check values before you send them

A wrong value gives you an API error. You can fix it in your own code first. A **clamp** keeps a number inside a range.

### Step by step: clamp a percentage

Keep a number between 0 and 100:

1. If it is below the minimum, give back the minimum.
2. If it is above the maximum, give back the maximum.
3. Otherwise give it back unchanged.

```python
def clamp_percent(x):
    if x < 0:
        return 0
    if x > 100:
        return 100
    return x

clamp_percent(-5)    # -> 0
clamp_percent(250)   # -> 100
clamp_percent(42)    # -> 42
```

In the first exercise you do the same for temperature, with a different range.

## Choosing settings by task

Instead of choosing numbers on every call, name your tasks and keep the settings in one place:

```python
SETTINGS = {
    "extract": {"temperature": 0, "max_completion_tokens": 200},
    "chat": {"temperature": 0.7, "max_completion_tokens": 500},
}

SETTINGS["chat"]    # -> {'temperature': 0.7, 'max_completion_tokens': 500}
```

An unknown task name should raise a clear error instead of silently using a wrong setting. In the second exercise you build this.

## Try it live

Send the same prompt three times with `temperature=0`, then three times with `temperature=1.5`. Prompt: *"Give me a name for a pet fish."* Compare the answers. At `0` they should be nearly the same. At `1.5` they should differ, and may get odd.

Then set `max_completion_tokens=10` and look at `finish_reason`.

## A little deeper

- **How temperature works.** The model's scores are divided by the temperature before they become chances. A small temperature makes the top choice much stronger. At exactly `0` the model always takes the top choice.
- **Temperature 0 is not always the same answer.** The servers do maths in parallel, and tiny differences can change a close choice. It is *mostly* stable, not perfectly.
- **Length is not the same as quality.** A small `max_completion_tokens` does not make the model write a *shorter, complete* answer. It cuts the answer off. To get a short answer, ask for it in the prompt, and use the limit as a safety net.
- **Penalties.** `frequency_penalty` and `presence_penalty` push the model away from repeating words. You rarely need them.
- **Input is limited too.** `max_completion_tokens` only limits the answer. The input limit is the context window (lesson 2).
- **Reasoning models** have extra settings for how much to "think", and their thinking also uses output tokens (lesson 34). The idea is the same: settings change the style of the answer, not what the model knows.

## Common mistakes

- Setting both `temperature` and `top_p`.
- Using a high temperature for tasks that need exact answers.
- Not checking `finish_reason`, so a cut-off answer looks complete.
- Expecting `seed` to guarantee identical output.
- Setting `max_completion_tokens` very small, then wondering why answers stop in the middle.

## Interview corner

**What does temperature do?**
It controls randomness when the model picks the next token. Low is steady and focused. High is varied and riskier.

**What temperature do you use for data extraction? Why?**
Low, usually 0, so the output is consistent and the model does not invent details.

**What is the difference between top_p and top_k?**
top_k keeps a fixed number of the most likely tokens. top_p keeps as many tokens as needed to reach a total chance of p.

**Why set a maximum number of output tokens?**
To control cost and latency, and to stop runaway answers. You must also handle `finish_reason == "length"`, because the answer may be cut off.

**Is temperature 0 fully deterministic?**
Not guaranteed. It is very stable, but tiny numeric differences on the server can still change a close choice.

## Summary

- The model draws the next word from a list of chances. Settings change how it draws.
- `temperature` 0 to 2: low is steady, high is creative.
- `max_completion_tokens` caps the answer length. A cut answer has `finish_reason == "length"`.
- `top_p` and `top_k` remove unlikely words first. Change temperature or top_p, not both.
- `stop` ends the answer at a given text. `seed` is a best-effort repeat.
- `**params` spreads a dictionary into named arguments.
- Clamp or validate values before sending them.
- Reference: `reference/genai-groq.md`.
