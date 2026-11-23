---
title: Prompt patterns
summary: Learn the patterns that make a model answer well and the same way each time - clear instructions, roles, examples, delimiters, output format and "say I don't know".
plan_ids: []
---

The model does exactly what the text in front of it suggests. The same model can give a bad answer or a great one, only because of how you asked. Writing the ask is called **prompt design**, or **prompt engineering**.

A **prompt** is all the text you send: the system message, the history and the new question. In lesson 1 you learned that the model continues the text it is given. A good prompt is text that makes the **best continuation** the answer you want.

In this lesson you learn six patterns, then two ways to get better answers on hard questions. You will use them again and again.

## 1. Be clear and specific

A vague ask gets a vague answer.

```
Bad:   "Tell me about this API."
Better: "Explain in 2 sentences what this API does, for a beginner."
```

Say **what** you want, **who** it is for, and **how long** it should be. Treat the model like a new colleague who has never seen your project: it only knows what you write.

## 2. Give it a role

A role in the system message sets the voice and the level.

```python
system = "You are a senior backend engineer. Explain things simply, with one short example."
```

A role does not make the model know more. It changes how it answers.

### Writing a good system prompt

The system message (lesson 4) is the most important prompt in your app, because it is sent with every call. A good one has four parts, in this order:

1. **Role**: who the model is. ("You are a support agent for DevDocs.")
2. **Task**: what it must do. ("Answer questions about the API.")
3. **Rules**: what to do and what not to do. ("Use only the documents given. If you do not know, say so.")
4. **Format**: what the answer looks like. ("Reply in at most 3 sentences.")

```python
system = (
    "You are a support agent for DevDocs.\n"
    "Answer questions about the API using only the documents given.\n"
    "If the answer is not in the documents, reply exactly: I don't know.\n"
    "Reply in at most 3 sentences."
)
```

Keep it short and put the most important rule first or last. Test it with 10 real questions before you trust it.

## 3. Show examples (few-shot)

Sometimes it is easier to **show** than to explain.

- **Zero-shot**: no examples. You only give the instruction.
- **Few-shot**: you give a few examples of input and the output you want.

Examples are the strongest way to fix the **format** and the **style** of the answer.

You can write the examples as fake chat turns. A `user` message holds the example input. An `assistant` message holds the answer you want. Then your real question comes last:

```python
messages = [
    {"role": "system", "content": "Label the sentiment as positive or negative."},
    {"role": "user", "content": "I love this!"},
    {"role": "assistant", "content": "positive"},
    {"role": "user", "content": "This is awful."},
    {"role": "assistant", "content": "negative"},
    {"role": "user", "content": "Great service, will come back."},   # the real question
]
```

The model sees two solved examples and copies the pattern. It will most likely answer `positive`, and nothing else.

### Step by step: a few-shot builder

Write `examples_to_messages(examples)`. Each example is a pair `(input, output)`.

1. Make an empty list `messages`.
2. Loop over the pairs. Unpack each as `inp, out`.
3. For each pair, add a user message, then an assistant message. The order matters.
4. Return the list.

```python
def examples_to_messages(examples):
    messages = []
    for inp, out in examples:
        messages.append({"role": "user", "content": inp})
        messages.append({"role": "assistant", "content": out})
    return messages

examples_to_messages([("2+2", "4"), ("3+3", "6")])
# -> [{'role': 'user', 'content': '2+2'}, {'role': 'assistant', 'content': '4'},
#     {'role': 'user', 'content': '3+3'}, {'role': 'assistant', 'content': '6'}]
```

In the first exercise, you will put the system message first and the real question last around a list like this.

## 4. Use delimiters

When you send a document and an instruction in the same prompt, the model can mix them up. Wrap the document in **delimiters**: clear markers, such as `<document>` and `</document>`.

```python
prompt = (
    "Summarize the text between the tags in one sentence.\n\n"
    "<document>\n"
    f"{text}\n"
    "</document>"
)
```

This also helps against **prompt injection**: if the document says "ignore your rules", the model knows that this is only *data inside the tags*, not an instruction. (You will see this problem again in Level 5. Delimiters help, but they do not fully stop it.)

## 5. Say the output format

Tell the model exactly what the answer must look like.

```
"Answer with one word: positive, negative or neutral."
"Reply as a bullet list with at most 3 bullets."
"Reply with JSON only, with the keys name and age."   # lesson 9
```

When your code reads the answer, a fixed format is not a nicety, it is a must. And even then, **clean the answer** in code. Models add spaces, dots and capital letters.

```python
raw = "  Positive.\n"
cleaned = raw.strip().lower().strip(".")
print(cleaned)   # -> positive
```

## 6. Let it say "I don't know"

By default the model tries to answer, even when it should not. Give it a safe way out:

```
"Answer only from the text between the tags. If the answer is not there, reply exactly: I don't know."
```

This single line removes many hallucinations. It is the heart of RAG, which you will build in Level 4.

## Think step by step

For tasks with reasoning, such as maths or comparing options, asking the model to **reason first** often gives better answers:

```
"Think step by step, then give the final answer on a new line that starts with 'Answer:'."
```

The model writes its reasoning as tokens, and each token helps the next one. Then you can read only the last line:

```python
reply = "First 12 + 8 = 20. Then 20 / 4 = 5.\nAnswer: 5"
last_line = reply.split("\n")[-1]
print(last_line)   # -> Answer: 5
```

## Hard questions: vote across several answers (self-consistency)

A model can give a wrong answer to a hard question once, and a right answer the next time. So for important questions, **ask several times and take the answer that comes up most**. This is called **self-consistency**. It is like asking five friends and going with the majority.

It needs a higher temperature, so the answers differ, and it costs more (one call per answer). Use it when being right matters more than being cheap.

The counting part is a **counter-dict**. Let's practise it with a different example: votes for a colour.

1. Make an empty dictionary `counts = {}`.
2. For each vote, add 1 to its count (`.get(vote, 0) + 1`).
3. Find the vote with the biggest count. If there is a tie, the first one that reached the top stays.

```python
votes = ["red", "blue", "red", "green", "red"]
counts = {}
for vote in votes:
    counts[vote] = counts.get(vote, 0) + 1

best = None
best_count = 0
for vote, count in counts.items():
    if count > best_count:
        best = vote
        best_count = count

print(counts)   # -> {'red': 3, 'blue': 1, 'green': 1}
print(best)     # -> red
```

You will clean and count model answers in the fourth exercise.

## Putting it together: a classifier

Common job: put a text into one of a fixed list of labels. The pattern:

1. The prompt lists the labels and says "answer with only the label".
2. Call the model with a low temperature.
3. **Clean** the reply (`strip`, `lower`, remove a final dot).
4. If the cleaned reply is one of the labels, return it. Otherwise return `"unknown"`. Do not trust that the model obeyed.

```python
def pick_label(reply, labels):
    cleaned = reply.strip().lower().strip(".")
    if cleaned in labels:
        return cleaned
    return "unknown"

pick_label("  Positive.\n", ["positive", "negative"])    # -> 'positive'
pick_label("I think it is great!", ["positive", "negative"])   # -> 'unknown'
```

Step 4 is the habit that separates a demo from real code: **never trust the model's format. Check it.**

## Try it live

In code (or the Playground), send this to your model three times at `temperature=1`:

*"A shop has 23 apples. It sells 9, then gets 14 more, then sells half of what it has. How many are left? Think step by step, then write 'Answer:' and the number."*

Do all three answers agree? Now do the same with `temperature=0`. Then remove the "Think step by step" part and compare. Write down what you see.

## A little deeper

- **Order matters.** Put the long document first and the question last, or the instruction at both ends. Models can lose track of the middle of a long prompt.
- **Positive instructions work better.** "Answer in one sentence" works better than "Do not write long answers".
- **Prompts are code.** Keep them in files, review them, test them, and change them one thing at a time. Lesson 8 shows how.
- **Chain of thought is not magic.** Newer "reasoning" models do it for you inside. Telling them to think step by step adds little.
- **Few-shot examples bias the output.** If all your examples are "positive", the model will lean positive. Mix them, and keep the order varied.
- **Prompt injection.** Text that comes from users or documents can contain hidden instructions. Treat it as data. Delimiters are the first, small defence.

## Common mistakes

- Vague asks: "make it better".
- Trusting the output format without checking it.
- Putting instructions and data in one blob with no delimiters.
- A long list of "don't"s and no example of what you do want.
- Changing five things in the prompt at once, so you do not know which one helped.
- Few-shot examples that are all the same label.

## Interview corner

**What is the difference between zero-shot and few-shot prompting?**
Zero-shot gives only an instruction. Few-shot adds a few input and output examples, which fix the format and style.

**How do you get a model to answer in a fixed format?**
Say the format in the prompt, show an example, set a low temperature, and validate the reply in code (and retry or fall back if it is wrong).

**Why use delimiters around documents?**
They separate data from instructions. That makes the prompt clearer and helps (a little) against prompt injection.

**What is self-consistency?**
Ask the same hard question several times at a higher temperature and choose the most common final answer. It improves accuracy at the cost of more calls.

**How do you reduce hallucinations with prompting?**
Give trusted context, tell the model to answer only from it, and give it an exact "I don't know" reply for when the answer is missing.

## Summary

- Be clear: what, for whom, how long. Add a role in the system message.
- Few-shot: show examples as `user` and `assistant` turns.
- Delimiters (`<document>...</document>`) separate data from instructions.
- Say the output format, then **clean and check** the reply in code.
- Give an exact "I don't know" reply for missing answers.
- For reasoning, ask for steps, then a final `Answer:` line.
- A good system prompt has a role, a task, rules and a format.
- Self-consistency: ask several times and take the most common answer. It is slower and costs more.
- Reference: `reference/genai-groq.md`.
