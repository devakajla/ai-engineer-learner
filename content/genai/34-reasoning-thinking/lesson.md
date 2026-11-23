---
title: Reasoning models and thinking output
summary: Learn what a thinking (reasoning) model is, how its thinking text shows up in the reply, how to separate it from the answer, and what it costs.
plan_ids: []
---

In lesson 32 you met **reasoning models**: chat models trained to think before they answer. Some models you will call, including the Qwen family, can do this. This lesson shows what that looks like in your code, and what you must handle so your app does not break.

Why does this matter? Because a thinking model sends back **more than the answer**. If your code treats the whole reply as the answer, your users may see the model's private notes. And you pay for those notes.

## What does "thinking" mean?

When you ask a hard question, a person often thinks it through before answering. A reasoning model does the same, but its thinking is **written text**: a long scratch pad of tokens. Then it writes the final answer.

```
Question: A shop has 23 apples. It sells 9, gets 14 more, then sells half. How many are left?

[thinking]  23 - 9 = 14. 14 + 14 = 28. Half of 28 is 14. Check: ...
[answer]    14 apples are left.
```

Why does writing help? Each token the model writes helps it write the next one (lesson 7, "think step by step"). A reasoning model does this on purpose, a lot, before it commits to an answer.

## Where does the thinking text go?

It depends on a setting. Many providers, including Groq for models that think, let you choose how the thinking is returned. The setting is often called `reasoning_format`. Typical choices:

| Setting | What you get |
| --- | --- |
| `raw` | The thinking is **inside** `message.content`, between `<think>` and `</think>` tags, then the answer. |
| `parsed` | The thinking is in a **separate** field (for example `message.reasoning`). `content` has only the answer. |
| `hidden` | The thinking is **removed**. You still pay for it. |

> Names and support differ by model and change over time. Check the Groq docs page for reasoning (`console.groq.com/docs/reasoning`) and the page of the model you use.

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    reasoning_format="parsed",    # check that your model supports this
)
message = response.choices[0].message
print(message.content)      # -> just the answer
print(message.reasoning)    # -> the thinking text
```

Because settings differ, your code should be ready for **both** shapes: thinking inside the content, or in a separate field. You will write that in the second exercise.

## Splitting the thinking from the answer

When the thinking comes inside the content, it looks like this:

```
<think>
23 - 9 = 14 ...
</think>
14 apples are left.
```

You need the part before `</think>` and the part after it. Let's learn the pattern with a different example: a note in square tags, like `[note] ... [/note]`.

Steps:

1. Look for the opening tag and the closing tag in the text with `.find(...)`. It returns the position, or `-1` if the text is not there.
2. If there is no opening tag, there is no note. Return an empty note and the whole text.
3. Cut out the text between the tags. That is the note.
4. The rest after the closing tag is the main text.

```python
def split_note(text):
    start = text.find("[note]")
    end = text.find("[/note]")
    if start == -1 or end == -1:
        return "", text.strip()
    note = text[start + len("[note]"):end].strip()
    main = text[end + len("[/note]"):].strip()
    return note, main

split_note("[note] be kind [/note] Hello!")   # -> ('be kind', 'Hello!')
split_note("Hello!")                          # -> ('', 'Hello!')
```

`text[a:b]` cuts a slice from position `a` up to (not including) `b`. `len("[note]")` is how many characters the opening tag has, so we start right after it.

The first exercise asks for the same split with `<think>` and `</think>`, and one extra rule about a tag that never closes.

## What thinking costs

Thinking text is made of **output tokens**. You pay for them, and they use up your `max_completion_tokens` budget and your time.

Three effects:

1. **Cost.** A short answer may come with a long thinking text. Output tokens are the more expensive kind (lesson 2).
2. **Speed.** The model writes the thinking before the answer. The first useful word comes late. Streaming (lesson 6) shows thinking first.
3. **Cut-off.** If `max_completion_tokens` is small, the model may use all of it on thinking and never reach the answer. You then get an empty or half answer, with `finish_reason == "length"` (lesson 5).

So give a thinking model a bigger token budget than a normal one.

You can estimate how much of the output was thinking with your `estimate_tokens` function from lesson 2. The third exercise does that.

## When to use a thinking model

Use thinking when the task is **hard**: maths, logic, tricky code, multi-step planning, comparing options.

Do not use it for easy tasks: classify a short text, pull out a date, rewrite a sentence. A normal model is faster and cheaper there, and thinking adds nothing. Choosing per task is the **routing** idea from lesson 33.

Some thinking models let you turn thinking down or off for a call (for example, a `reasoning_effort` setting). That can save money. Check what your model supports.

## Try it live

1. Ask your default model: *"A shop has 23 apples. It sells 9, gets 14 more, then sells half. How many are left?"* Print `response.choices[0].message.content`. Do you see a `<think>` block?
2. Print `response.usage.completion_tokens`. Now ask a very easy question ("Say hi") and compare the token counts.
3. Try `reasoning_format="parsed"`, then `"hidden"`. What changes? If the API returns an error, read it: it may tell you which values the model supports.
4. Set `max_completion_tokens=50` and ask the apples question. What is in the reply, and what is `finish_reason`?

## A little deeper

- **Thinking is not a promise.** The thinking text is a model-written draft. It can contain errors, and it may not show the real reason for the answer. Do not show it to users as "proof".
- **Do not send thinking back.** When you build the history (lesson 4), keep only the final answer. Old thinking only costs input tokens.
- **Streaming and thinking.** With raw thinking, the stream shows the `<think>` text first. Decide whether to hide it in your UI until the answer starts.
- **Safety.** Thinking text may include the content of private instructions. Do not expose it by default.
- **Temperature for thinking models.** Providers often advise a medium temperature, not 0, for reasoning models. Read the model card.

## Common mistakes

- Showing the raw reply to users, including `<think>` text.
- A small `max_completion_tokens`, so thinking eats it all and the answer is empty.
- Using a thinking model for easy tasks and paying for thinking you do not need.
- Putting old thinking text into the history.
- Assuming one `reasoning_format` works on every model.

## Interview corner

**What is a reasoning model?**
A chat model trained to write a long chain of thought before the final answer. It is better at hard multi-step problems, and slower and costlier.

**Where does the thinking text come from and what does it cost?**
It is output tokens the model writes before the answer. You pay for them, they add latency, and they can use up the token limit.

**How do you handle thinking text in an app?**
Request a format that separates it (or strip `<think>` tags in code), show only the final answer, keep thinking out of the history, and give a larger token budget.

**When should you not use a reasoning model?**
For simple tasks such as classification or extraction, where it adds cost and delay with no gain.

## Summary

- A reasoning model writes thinking tokens first, then the answer.
- The thinking may be inside `content` between `<think>` tags, or in a separate field, depending on `reasoning_format`.
- Split the two in code. Show only the answer. Keep thinking out of the history.
- Thinking uses output tokens: cost, delay, and a risk of running out of `max_completion_tokens`.
- Use thinking for hard tasks only. Route easy tasks to a normal model.
- Always check the docs of your model for the current settings.
