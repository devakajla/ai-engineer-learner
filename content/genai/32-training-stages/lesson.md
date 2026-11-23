---
title: How an LLM is trained, and why it makes things up
summary: See the three stages of training (pretraining, instruction tuning, preference tuning), the difference between base, chat and reasoning models, and the real reasons for hallucination.
plan_ids: []
---

In lesson 1 you learned that an LLM predicts the next token, and that training turns its dials. In this lesson we open that box a little more.

Why does an AI Engineer need this? Because every behaviour of a model, good or bad, comes from how it was trained. When you know the stages, you can explain *why* a model follows instructions, *why* it makes things up, and *why* it does not know today's news. Interviewers ask these questions often.

## The big picture: three stages

A chat model is built in three steps:

```
Stage 1: Pretraining         read huge text, learn to predict the next token
Stage 2: Instruction tuning  learn from examples of questions and good answers
Stage 3: Preference tuning   learn which answers humans like more
```

Think of a person. First they read thousands of books (stage 1). Then a teacher shows them how to answer exam questions properly (stage 2). Then they get feedback on which answers people prefer (stage 3).

## Stage 1: Pretraining

The model reads a huge amount of text: websites, books, code, articles. For every position in the text, it plays one game: **guess the next token**. It checks its guess against the real text and turns its dials a tiny bit to do better next time. It plays this game trillions of times.

After this stage, the model knows grammar, facts, styles and a lot about the world. But it only **continues text**. If you write "What is the capital of France?", it might continue with another question, because that is also how texts on the internet look. This is a **base model**.

### Pretraining in miniature: counting

You can build a toy version in a few lines. Instead of dials, we count. We read some text and count **which word follows which word**. The counts become the table you saw in lesson 1.

Let's practise the counting step with a different example: which **letter** follows which letter in a word. Take `"banana"`.

The pairs are `b→a`, `a→n`, `n→a`, `a→n`, `n→a`. Step by step:

1. Start with an empty dictionary `counts = {}`.
2. Go through the positions of the word, from the first up to the second-to-last. At each position, look at the letter and the letter right after it.
3. If the first letter is not yet in `counts`, give it an empty dictionary.
4. Add 1 to the count of the second letter inside the first letter's dictionary. Use `.get(x, 0)` so a new letter starts at 0.

```python
word = "banana"
counts = {}
for i in range(len(word) - 1):
    first = word[i]
    second = word[i + 1]
    if first not in counts:
        counts[first] = {}
    counts[first][second] = counts[first].get(second, 0) + 1

print(counts)   # -> {'b': {'a': 1}, 'a': {'n': 2}, 'n': {'a': 2}}
```

Read it: after `a`, the letter `n` appeared 2 times. After `b`, the letter `a` appeared once.

`len(word) - 1` is the key. The last letter has nothing after it, so we stop one early. This "look at a thing and its neighbour" pattern is called a **sliding pair**, and you will use it in the first exercise.

### From counts to chances

Counts are not chances yet. Chances must add up to 1. To get a chance, divide each count by the **total** of that row:

```python
row = {"n": 2, "x": 2}      # after "a": n twice, x twice
total = sum(row.values())   # -> 4
chances = {}
for letter, count in row.items():
    chances[letter] = round(count / total, 2)
print(chances)   # -> {'n': 0.5, 'x': 0.5}
```

`sum(row.values())` adds up all the counts. `round(value, 2)` keeps two decimal places.

Now you have the same kind of table as in lesson 1, but **learned from text** instead of typed by hand. Feed it to the `generate` idea from lesson 1 and you have a tiny "language model". It is weak, because it only looks at one word. A real LLM looks at thousands of tokens and has billions of dials. The idea is the same.

## Stage 2: Instruction tuning (SFT)

A base model only continues text. We want it to **follow instructions**. So the model is trained more, on many examples that look like this:

```
Question:  Explain what a variable is in one sentence.
Good answer: A variable is a name that points to a value.
```

Real people (and other models) write thousands of such question-and-answer pairs. The model trains on them with the same next-token game. This stage is called **SFT**, **supervised fine-tuning**. "Supervised" means the answers are given. "Fine-tuning" means small extra training on top of the big base model.

After SFT the model answers questions instead of just continuing them. It also learns the **chat format**: the `system`, `user` and `assistant` roles from lesson 4.

## Stage 3: Preference tuning (RLHF and DPO)

After SFT, the model can follow instructions, but its answers may be rude, unsafe, too long or just not great. To improve this, people compare answers.

1. The model writes two answers to the same question.
2. A human picks the better one.
3. The model is trained to produce more answers like the winner.

This is **RLHF**, reinforcement learning from human feedback. A newer, simpler method is **DPO**, direct preference optimisation. It uses the same "A is better than B" data but trains the model directly. You do not need the maths. You need the idea: **humans rank answers, and the model learns to write the kind of answers humans prefer**.

This stage also teaches **safety**: refusing harmful requests. It is why models are polite and careful.

## Three kinds of models you will see

| Kind | What it is | Typical use |
| --- | --- | --- |
| **Base** | Only stage 1. Continues text | Researchers, further training |
| **Chat / instruct** | Stages 1 to 3. Follows instructions | What you call through an API |
| **Reasoning** | A chat model trained to think step by step before the final answer | Hard maths, logic, planning, code |

A **reasoning model** first writes a long "thinking" text, then gives the answer. It is often better at hard problems. It is also slower and costs more, because the thinking uses output tokens.

The default model of this track, `qwen/qwen3.8-27b`, is a chat model. Some models of the Qwen family can also think before they answer, like a reasoning model. Check the model page on `console.groq.com/docs/models` to see what the model you use can do, since the list changes.

## Why models hallucinate

Now we can answer a favourite interview question: why does an LLM make things up?

1. **It predicts likely text, not true text.** Stage 1 never checks facts. A fluent false sentence looks just as good to the model as a true one.
2. **Gaps in its data.** If it saw a topic rarely, its dials hold a blurry memory. It fills the gap with likely-sounding words.
3. **Knowledge cutoff.** Training data stops on some date. Anything after that is unknown to the model.
4. **Training pushes it to answer.** In SFT, the examples are always good answers. In preference tuning, confident, helpful answers win. The model rarely learned to say "I don't know".
5. **Wrong or mixed sources.** The internet has errors. The model learned them too.
6. **Long answers drift.** Each token depends on the earlier ones. One small mistake early can lead the rest of the answer further away.

### What helps

- **Give it the facts** in the prompt (RAG). The model then copies from real text.
- **Allow "I don't know".** Tell the model it may say so.
- **Lower the temperature** for factual tasks (lesson 5).
- **Ask for sources**, then check them.
- **Check the output** with code where you can, like the `unsupported` check in lesson 1.

A model with more dials, better data and more preference tuning hallucinates less. It never reaches zero.

## Try it live

In the Groq Playground:

1. Ask a base-style trick: *"The capital of France is"* and watch if it simply finishes the sentence.
2. Ask: *"Who won the Nobel Prize in Physics last year?"* Does it say it is unsure, or does it guess?
3. Add *"If you are not sure, say you do not know."* and ask something obscure. Compare.

## A little deeper

- **Scale.** More dials, more data and more computing generally make a model better. The relation is smooth enough that companies plan it. This is called the **scaling idea**.
- **Distillation.** A big model can write answers that train a small model. The small model gets some of the big one's skill at lower cost. Many small, fast models are made this way.
- **Parameters count.** "8B" means 8 billion dials. "70B" is 70 billion. Bigger models are usually smarter, slower and costlier.
- **Fine-tuning for your own use.** You can run extra SFT on your own examples. It changes the model's style and format. It is a poor way to teach new facts. Use RAG for facts. (Level 5 covers fine-tuning ideas.)
- **Synthetic data.** Today, much SFT data is written by other models and then checked.
- **Reasoning models** are often trained with a reward for correct final answers, so they learn to think longer when it helps.

## Common mistakes

- Thinking the model "knows" your data because you fine-tuned it. Fine-tuning changes style, not reliable facts.
- Expecting a base model to follow instructions.
- Using a reasoning model for easy tasks and paying for thinking you do not need.
- Believing that more training removes hallucinations. It reduces them.

## Interview corner

**What are the stages of training an LLM?**
Pretraining on a lot of text (predict the next token), instruction tuning (SFT) on question-answer examples, then preference tuning (RLHF or DPO) using human rankings of answers.

**What is the difference between a base model and a chat model?**
A base model only continues text. A chat model went through SFT and preference tuning, so it follows instructions and the chat format.

**What is RLHF?**
Humans compare model answers. A reward signal is built from their choices. The model is trained to produce answers humans prefer.

**Why do LLMs hallucinate?**
They predict likely text, not true text. They have gaps and a knowledge cutoff, and training rewards confident answers. Giving trusted context (RAG), allowing "I don't know", and checking outputs reduce it.

**Should you fine-tune to add knowledge?**
Usually no. Fine-tuning is good for style, format and behaviour. For fresh or private facts, retrieve them and put them in the prompt.

## Summary

- Stage 1 pretraining: learn to predict the next token from huge text. Result: a base model.
- Stage 2 SFT: learn from question-answer examples. Result: follows instructions.
- Stage 3 RLHF or DPO: learn from human preferences. Result: helpful and safe style.
- Base, chat and reasoning models are different tools. Reasoning models think first and cost more.
- Counting which word follows which is pretraining in miniature: counts become chances.
- Hallucination comes from predicting likely text, data gaps, the cutoff and training that rewards answering.
- Fix it with trusted context, "I don't know" permission, low temperature and checks.
