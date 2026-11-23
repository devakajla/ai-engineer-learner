# 6. Prompt engineering

A **prompt** is the whole input you give the model. The model cannot read your mind: it only has your text. **Prompt engineering** is writing that text so the model reliably does what you need. It is less magic than it sounds. It is mostly clear writing, plus a few proven patterns.

## The core idea

Imagine giving a task to a very fast, very literal new colleague who knows nothing about your project. If you say "write about our product", you get something generic. If you say who the reader is, what to include, what to avoid, and what the result should look like, you get something useful. Prompting is the same.

A good prompt answers five questions:

@@ grid 3 | Figure 6.1: the parts of a strong prompt.
Role|who should the model be?;"You are a support agent for..."|blue
Task|what exactly to do?;one clear verb|green
Context|facts it needs;the document, the user's data|yellow
Rules|limits and style;length, tone, what not to do|red
Format|the shape of the answer;a list, JSON, two sentences|purple
@@ end

## Where things go

- **System message:** the role, the rules and the format. Things that hold for every turn.
- **User message:** the task and the specific data for this turn.

Put long reference text in the user message, **clearly separated** from instructions, using markers:

```python
system = (
    "You are a support assistant for the app TaskFlow. "
    "Answer only from the text between <docs> tags. "
    "If the answer is not there, say: I do not know. "
    "Reply in at most 3 sentences."
)
user = f"<docs>\n{doc_text}\n</docs>\n\nQuestion: {question}"
```

Delimiters like `<docs>` help the model see where the data ends and the instructions begin. This also reduces **prompt injection**, which is when text inside the data tries to give the model new orders (chapter 17).

## Patterns that work

### 1. Be specific

| Weak | Strong |
| --- | --- |
| "Summarise this." | "Summarise this email in 3 bullet points for a busy manager. Start with the decision needed." |
| "Make it better." | "Fix grammar and cut it to 80 words. Keep a friendly tone." |

### 2. Say what to do, not only what not to do

"Do not be long" is vague. "Use at most two sentences" is checkable.

### 3. Few-shot examples

Models learn patterns from **examples** inside the prompt. Showing two or three input and output pairs is often stronger than long explanations. This is called **few-shot** prompting. With no examples it is **zero-shot**.

```python
messages = [
    {"role": "system", "content": "Classify the sentiment as positive, negative or neutral. Reply with one word."},
    {"role": "user", "content": "I love this app"},
    {"role": "assistant", "content": "positive"},
    {"role": "user", "content": "It crashed twice today"},
    {"role": "assistant", "content": "negative"},
    {"role": "user", "content": "The update is okay I guess"},
]
```

The two earlier turns are fake history that **teach the format**. The model now answers the last message with one word, in the same style. Pick examples that are varied, correct and close to real inputs, because the model copies their quirks.

### 4. Give the model room to think (chain of thought)

For maths, logic and multi-step problems, asking the model to **reason step by step before answering** improves accuracy. Writing the steps gives the model "space" to compute.

```
Solve the problem. Think step by step, then give the final answer on a last line that starts with "Answer:".
```

Then your code reads only the line after `Answer:`. The cost: more output tokens. Some newer "reasoning" models do this thinking internally, so check the model's docs before adding it.

### 5. Ask for a format

Say exactly how the answer should look: "a numbered list", "a table with columns name and price", or JSON (chapter 7). A fixed format makes the output easy for your code to use.

### 6. Break a big task into steps (prompt chaining)

One giant prompt that does five things is fragile. Better: several small calls, each doing one thing, where the output of one feeds the next. For example: extract facts, then check them, then write the reply. Each step is easier to test and fix.

### 7. Handle "I don't know"

Models want to answer. Give them a **permitted way out**: "If the text does not contain the answer, reply exactly: Not found." This single line reduces many hallucinations.

## Prompts are code: templates

Real apps build prompts from pieces. Keep the template in one place, with named holes:

```python
TEMPLATE = (
    "You are a {role}.\n"
    "Task: {task}\n"
    "Keep the answer under {max_words} words.\n\n"
    "Text:\n{text}"
)

prompt = TEMPLATE.format(
    role="careful editor",
    task="fix spelling mistakes only",
    max_words=50,
    text="Ths is a smple tezt.",
)
print(prompt.splitlines()[0])
# -> You are a careful editor.
```

Why a template? You can **version** it, **test** it, and change wording without touching the logic. Treat prompts like code: keep them in files, review changes, and measure the effect with evaluations (chapter 16). A tiny wording change can move quality a lot, in either direction.

## Prompt caching

Many requests start with the **same long prefix** (a big system prompt, or a document). Some providers can **cache** that prefix, so repeated calls are cheaper and faster. To benefit, put the **fixed part first** and the **changing part last**. Check your provider's docs on how caching is priced and triggered.

## A method for improving a prompt

@@ flow | Figure 6.2: the prompt loop.
Write v1|clear and simple|blue -> Try 10 real inputs|include hard ones|yellow -> See failures|what went wrong, exactly?|red -> Change one thing|an instruction or an example|green
@@ end

Never judge a prompt on one example. Keep a small set of test inputs and re-run them after every change. Chapter 16 makes this a proper evaluation.

::: {.box .checkpoint}
**Checkpoint:** given a vague prompt, you can rewrite it with role, task, context, rules and format, and you can say when you would add examples.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Vague instructions ("make it good").
- Hiding the real task in the middle of a long block of text.
- Mixing instructions and data with no separators.
- Judging a prompt on a single lucky example.
- Giving only positive examples of one kind, so the model always copies them.
- No way out for "I don't know".
- Editing the prompt and not recording what changed.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Zero-shot vs few-shot?** Zero-shot gives only instructions. Few-shot adds example input and output pairs to show the pattern.

**Q: What is chain of thought prompting?** Asking the model to reason step by step before answering, which improves multi-step accuracy at the cost of tokens.

**Q: How do you reduce hallucinations through the prompt?** Provide the facts, tell it to use only them, give an explicit "not found" answer, and ask for quotes or citations.

**Q: Where do instructions go, system or user?** Standing rules, role and format go in the system message. Task-specific data goes in the user message.

**Q: How do you evaluate a prompt change?** Run it on a fixed test set, compare scores to the previous version, and look at the failures.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Rewrite "Explain Docker" as a prompt with role, task, rules and format for a complete beginner.
2. Build a few-shot classifier that labels support emails as `billing`, `bug` or `other`. Test it on five emails.
3. Write a prompt that answers only from a given paragraph and says `Not found` otherwise. Test with a question that is not in the paragraph.
4. Make a template with `{name}` and `{tone}` holes, and print it for two different inputs.
5. Take one prompt and change it three times. Record which version fixed which failure.
6. **Think:** why is putting the document and the question in separate, marked sections safer than one block of text?
:::
