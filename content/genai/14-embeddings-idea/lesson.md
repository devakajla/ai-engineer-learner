---
title: The idea of embeddings
summary: Learn how text becomes a list of numbers (an embedding), why similar meanings end up close together, and how to compare two embeddings with a dot product and a distance.
plan_ids: []
---

In Levels 1 and 2 the model answered from **its own memory**, or from a document you pasted into the prompt. That does not scale. A real API has hundreds of pages of docs. You cannot paste them all into every prompt (lesson 2: the context window is limited, and you pay for every token).

So you need **search**: find the few pieces of text that matter for a question, and send only those. Level 3 is about building that search. Level 4 plugs it into the model, and that is **RAG**.

The first problem is: how does a computer search by **meaning**?

## Keyword search is not enough

Imagine your docs say: "Remove a task with the DELETE endpoint." A user asks: "How do I get rid of a todo item?"

The words are different: "remove" vs "get rid of", "task" vs "todo item". A keyword search finds nothing. But a human sees that both mean the same.

We need a way to turn text into something a computer can compare by **meaning**. That something is an **embedding**.

## What is an embedding?

An **embedding** is a list of numbers that stands for a piece of text. It is made by an **embedding model**.

```python
embed("Remove a task")   # -> [0.12, -0.53, 0.08, 0.77, ...]   (many numbers)
```

A list of numbers like this is also called a **vector**. Three facts to remember:

1. **Fixed length.** A short word and a long paragraph both become a vector of the same length. That length is called the **dimension**. Common sizes: 384, 768, 1536.
2. **Meaning is position.** The model was trained so that texts with a similar meaning get vectors that are **close** to each other. "Remove a task" and "delete a todo item" land near each other. "The weather is sunny" lands far away.
3. **The numbers alone mean nothing.** You cannot read "0.12" and know what it stands for. Only the **distance between vectors** is useful.

Think of a map. Each text is a point on the map. Close points have similar meaning. A search becomes: "put the question on the map, and find the nearest points."

A real map has 2 dimensions. An embedding space has hundreds. The idea is the same.

## A toy embedder, to see the idea

You do not need a model to understand the shape of the thing. A very simple embedder: choose a **vocabulary** (a fixed list of words), and for each word count how often it appears in the text.

Here is a different small version: count how often each **letter** from a list appears. (We use letters here so you can focus on the pattern. In the exercise you will count whole words.)

Steps:

1. Make an empty list `counts`.
2. For each letter in the list, count how many times it appears in the text, with `text.count(letter)`.
3. Add that number to `counts`.
4. Return `counts`. Its length always equals the length of the letter list.

```python
def letter_counts(text, letters):
    counts = []
    for letter in letters:
        counts.append(text.count(letter))
    return counts

letter_counts("banana", ["a", "b", "z"])    # -> [3, 1, 0]
letter_counts("", ["a", "b", "z"])          # -> [0, 0, 0]
```

Whatever text you give, you get a vector with exactly 3 numbers. That is the "fixed length" fact, in a tiny form.

The word version in the exercise has one more step: first cut the text into words (`text.lower().split()`), and strip punctuation from the ends of each word.

A toy like this still has a big weakness: it knows nothing about meaning. "remove" and "delete" are two unrelated columns. Real embedding models fix this, because they learned from huge amounts of text which words and phrases are used in similar ways.

## Real embedding models

Two kinds:

- **Local models**: you run them on your own computer. Free, private, work offline after the first download. Example: `BAAI/bge-small-en-v1.5` (384 dimensions), run with the `fastembed` library.
- **API models**: you send text to a provider (OpenAI, Cohere, Voyage and others) and pay per token.

For learning, we use a **local** model. No key, no cost, no limits.

> Does Groq have an embeddings API? Sources disagree, and I could not confirm it in the official docs. Check `console.groq.com/docs` yourself. This track does not depend on it: the local model works with any LLM provider.

Using `fastembed`:

```python
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")        # downloads about 130 MB the first time
vectors = list(model.embed(["Remove a task", "The weather is sunny"]))
print(len(vectors))        # -> 2         (one vector per text)
print(len(vectors[0]))     # -> 384       (the dimension)
```

Install it with `uv add fastembed`. The step-by-step project (below) wraps it in one small function.

## One important rule

**Use the same embedding model for the documents and for the question.** Vectors from different models live in different "maps". Comparing them is meaningless.

It also means: if you change the model later, you must **embed all your documents again**.

## Comparing two vectors

We need a number that says "how close are these two vectors?" Two common ones. Both use two lists `a` and `b` of the same length.

### Dot product

Multiply the numbers in the same positions, then add everything up.

```python
a = [1, 2, 3]
b = [4, 5, 6]
# 1*4 + 2*5 + 3*6 = 4 + 10 + 18
print(sum(x * y for x, y in zip(a, b)))   # -> 32
```

`zip(a, b)` walks both lists together, and gives pairs `(1, 4)`, `(2, 5)`, `(3, 6)`. The bigger the dot product, the more the vectors "point the same way" (for vectors of the same size).

### Euclidean distance

This is the straight-line distance, the one from school. For each position take the difference, square it, add them up, and take the square root:

```python
a = [0, 0]
b = [3, 4]
# (3-0)**2 + (4-0)**2 = 9 + 16 = 25, and the square root of 25 is 5
print(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5)   # -> 5.0
```

A power of `0.5` is the same as a square root. Here a **small** number means **close**. A distance of 0 means the vectors are the same.

If the two lists have different lengths, the comparison makes no sense. `zip` would quietly stop at the shorter list and hide the bug. So check the lengths first and raise a `ValueError`.

Next lesson adds a better measure, **cosine similarity**, which is the one almost everybody uses for text.

## Functions are values: passing `embed` around

In the exercises and in the project, you will write code like this:

```python
def embed_all(texts, embed):
    return embed(texts)
```

Here `embed` is a **function** that is passed in as an argument. In Python a function is a value, like a number or a string. You can put it in a variable, and pass it to another function. You call it with `()` inside.

```python
def shout(text):
    return text.upper()

def apply_twice(text, fn):
    return fn(fn(text))

print(apply_twice("hi", shout))   # -> HI
```

Note: you write `shout` (no brackets) to **pass** the function, and `fn(...)` to **call** it.

Why do this? The same reason you passed the `client` in Level 1: **tests**. In real code you pass the real embedding model. In tests you pass a tiny fake function, so tests are fast and need no download. You will see this in every project step of this level.

## Your first search: find the nearest text

You now have both parts of a search: a way to turn text into a vector, and a way to measure the distance between two vectors. A search is just **"embed everything, then take the closest"**.

Let's practise the pattern with a different example: find the closest **number** to a target.

1. Start with no best answer yet (`None`).
2. For each candidate, measure its distance to the target.
3. If it is the first one, or it is closer than the best so far, it becomes the best.
4. Return the best. An empty list gives `None`.

```python
def closest_number(target, numbers):
    best = None
    best_distance = None
    for n in numbers:
        distance = abs(n - target)
        if best_distance is None or distance < best_distance:
            best = n
            best_distance = distance
    return best

closest_number(10, [3, 9, 20])   # -> 9
closest_number(10, [])           # -> None
```

Because we use `<` (not `<=`), a tie keeps the **earlier** item. In the fourth exercise you do the same with texts: the "number" is a vector, and the distance is `euclidean`.

## Try it live

1. Install `fastembed` (`uv add fastembed`) and embed these four texts: *"Remove a task"*, *"Delete a todo item"*, *"The weather is sunny"*, *"How do I log in?"*.
2. Print each vector's length (384). Use your `dot` to compare the first text with each of the others. Which one scores highest?
3. Compare the toy embedder with the real one on *"Remove a task"* and *"Delete a todo item"*. The toy one sees no link. The real one does.

## A little deeper

- **How a model makes embeddings.** It is a neural network, trained so that texts that appear in similar contexts get nearby vectors. A transformer reads the whole text and the vector is a summary of it. The model sees at most a limit of tokens (often 512), so long text must be cut up first. That is the next-but-one lesson (chunking).
- **Dimension is a trade-off.** More dimensions can hold more detail, but cost more memory, disk and search time. 384 is small and fast. 1536 and up is heavy.
- **Asymmetric models.** Some models want a different **prefix** for questions and for documents (for example, a "Represent this sentence for searching relevant passages:" prefix on the query for BGE models). Read the model card. A missing prefix lowers quality.
- **Multilingual models.** Some map Hindi and English to the same space, so a Hindi question can find an English page.
- **Embeddings are not only for text.** Images, audio and code have embeddings too. The idea of "close means similar" is the same.
- **Embeddings are not private by magic.** They can leak information about the text. Treat them like the text itself.
- **Benchmarks.** The MTEB leaderboard compares embedding models. A bigger model is not always better for your data. Test on your own questions.
- **Cost.** With an API model you pay to embed every document once, and every question each time. With a local model it costs compute time only.

## Common mistakes

- Using one model for documents and another for questions.
- Comparing vectors of different lengths.
- Forgetting the model's prefix rule.
- Expecting a toy bag-of-words vector to understand synonyms.
- Sending a very long text and expecting the whole text to be in the vector. The model cuts it off.
- Re-embedding the same unchanged documents on every run. Embed once, and store the result.

## Interview corner

**What is an embedding?**
A fixed-length vector of numbers that represents a text, made by a model so that texts with similar meaning are close to each other.

**Why do embeddings beat keyword search for some questions?**
They match meaning, not exact words. "Get rid of a todo" can find "Delete a task". (Keyword search still wins for exact terms like error codes. Lesson 18 combines both.)

**Can you compare embeddings from two different models?**
No. Each model has its own space. Use one model for both documents and queries, and re-embed everything if you change it.

**What does the dimension of an embedding tell you?**
How many numbers are in the vector. A higher dimension can hold more detail, but needs more memory and compute.

## Summary

- An embedding is a fixed-length vector that stands for a text. Close vectors mean similar meaning.
- Use a local model (`fastembed`, `BAAI/bge-small-en-v1.5`, 384 dimensions) for learning. Use the same model for documents and queries.
- Dot product: multiply in pairs and add (`sum(x * y for x, y in zip(a, b))`). Euclidean distance: the square root of the sum of squared differences.
- Check that vectors have equal length before you compare them.
- A function can be passed as an argument. Pass a fake `embed` in tests.
- Project: step 8 starts the retrieval part of DevDocs Copilot (with lesson 15).
- Reference: `reference/genai-retrieval.md`.
