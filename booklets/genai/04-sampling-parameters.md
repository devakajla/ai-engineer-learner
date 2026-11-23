# 4. Controlling the output: temperature, top-p and friends

The same prompt can give different answers. That is not a bug. Chapter 1 showed that the model gives **odds** for the next token, and then one token is **picked** by those odds. The settings in this chapter control *how that pick is made*, and when to stop.

## From scores to odds: softmax

For each next token, the model first produces a raw **score** (called a *logit*) for every token in its vocabulary. These are turned into probabilities that add up to 1 by a function called **softmax**. Then one token is sampled.

## Temperature: how adventurous

**Temperature** reshapes those odds before the pick. See it with three tokens that have scores 2.0, 1.0 and 0.1:

```python
import numpy as np

logits = np.array([2.0, 1.0, 0.1])

def softmax(scores, temperature):
    e = np.exp(scores / temperature)
    return e / e.sum()

for t in (0.2, 1.0, 2.0):
    print(t, np.round(softmax(logits, t), 3))
# -> 0.2 [0.993 0.007 0.   ]
# -> 1.0 [0.659 0.242 0.099]
# -> 2.0 [0.502 0.304 0.194]
```

Read the three rows:

- **Low temperature (0.2):** the top token gets 99.3 percent. The model almost always picks the most likely one. Output is steady and predictable.
- **Temperature 1.0:** the original odds.
- **High temperature (2.0):** the odds flatten, so unlikely tokens get a real chance. Output becomes varied, creative, and sometimes strange.

@@ grid 3 | Figure 4.1: temperature changes the shape of the odds.
Low (0 to 0.3)|peaked: same answer each time;good for facts, code, extraction|blue
Medium (0.5 to 0.8)|balanced;good for chat and summaries|green
High (1.0 and more)|flat: surprising answers;good for brainstorming and stories|yellow
@@ end

Temperature `0` means "always pick the top token" (called **greedy**). It is the most repeatable setting, though even then, some APIs do not promise identical output every time.

**Rule of thumb for engineers:** use a **low** temperature (0 to 0.3) for anything where the answer must be correct or in a fixed format: extraction, classification, code, JSON, RAG answers. Raise it only when you want variety.

## Top-p: cut off the unlikely tail

**Top-p** (also called *nucleus sampling*) keeps only the **smallest group of top tokens whose probabilities add up to p**, and ignores the rest.

```python
probs = np.array([0.5, 0.3, 0.15, 0.05])
cumulative = np.cumsum(probs)
print(cumulative)
# -> [0.5  0.8  0.95 1.  ]
print(int(np.searchsorted(cumulative, 0.9)) + 1)
# -> 3
```

With `top_p = 0.9`, the running totals are 0.5, 0.8, 0.95. We need three tokens to reach 0.9, so the fourth (5 percent) is **dropped**. Then the three remaining are re-scaled and one is sampled.

Why use it? It stops very unlikely tokens from ever being chosen, but still lets the number of choices adapt: when the model is sure, few tokens stay, and when it is unsure, more stay. Advice: **change temperature or top-p, not both.** Most people just set temperature and leave `top_p` alone.

## Other controls

| Parameter | What it does | When |
| --- | --- | --- |
| `max_completion_tokens` | hard cap on output length | always set it, for cost and safety |
| `stop` | a string (or list) that ends generation when produced | end at `"###"` or at a blank line |
| `seed` | asks for repeatable sampling | testing, if the provider supports it |
| `frequency_penalty` | lowers the odds of tokens that were already used often | reduce repeated words |
| `presence_penalty` | lowers the odds of any token that already appeared | encourage new topics |
| `n` | how many answers to produce | pick the best of several (costs more) |

An example that uses several:

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "List three fruits, one per line."}],
    temperature=0.2,
    max_completion_tokens=40,
    stop=["\n\n"],
)
```

Here `stop=["\n\n"]` ends the answer at the first blank line. The stop text itself is not included in the output.

### Is `max_completion_tokens` a way to get short answers?

No, it is a **cutoff**, not a style. A model told "write about cats" with a limit of 20 tokens does not write a *short* piece. It writes the normal beginning and gets **chopped**. To get short answers, **ask** for them ("in two sentences") and keep the limit as a safety net above that.

## Choosing settings for tasks

| Task | Temperature | Notes |
| --- | --- | --- |
| classify a message | 0 | one word out; small limit |
| extract fields into JSON | 0 | chapter 7 |
| answer from documents (RAG) | 0 to 0.2 | repeatable and grounded |
| chat assistant | 0.5 to 0.7 | natural, not too wild |
| write marketing ideas | 0.9 to 1.2 | variety is the goal |

::: {.box .checkpoint}
**Checkpoint:** you can explain, without looking, what happens to the odds when temperature goes from 1.0 down to 0.2, and which setting you use for JSON extraction.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- A high temperature for factual or structured output.
- Setting both temperature and top-p, and not knowing which one caused a change.
- Using `max_completion_tokens` to make answers concise instead of asking.
- Expecting temperature 0 to be a guarantee of identical text.
- Forgetting the token cap, and paying for a runaway answer.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What does temperature do?** It scales the model's scores before softmax. Low values sharpen the distribution toward the top token, high values flatten it and add randomness.

**Q: Temperature vs top-p?** Temperature reshapes the whole distribution. Top-p cuts the tail, keeping the smallest set of tokens whose total probability reaches p.

**Q: Which settings do you use for a RAG answer?** A low temperature (0 to 0.2) for faithful, repeatable output, with a token cap.

**Q: Is temperature 0 deterministic?** It is the most repeatable choice, but hardware and batching can still cause small differences.

**Q: What is a stop sequence?** A string that makes generation end when the model produces it.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Run the softmax function with temperatures 0.1, 0.5, 1 and 3 on `[3.0, 1.0, 0.5]`. At which temperature does the top token fall below 60 percent?
2. For probabilities `[0.4, 0.3, 0.2, 0.1]` and `top_p = 0.7`, which tokens are kept?
3. Ask the model for a haiku three times at temperature 0 and three times at 1.2. Compare.
4. Use `stop` to make the model list only the first item of a numbered list.
5. **Think:** why is a high temperature dangerous for a customer-support bot that quotes refund rules?
:::
