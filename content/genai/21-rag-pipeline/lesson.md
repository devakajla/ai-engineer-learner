---
title: The RAG pipeline end to end
summary: Build retrieval-augmented generation from zero - why we need it, the two phases (index and query), how to put retrieved chunks in a prompt, and how to say "I don't know".
plan_ids: []
---

You now have two skills from earlier levels:

- **Level 1 and 2:** you can call a model and write good prompts.
- **Level 3:** you can search a pile of text by meaning.

**RAG** joins them. It stands for **Retrieval-Augmented Generation**:

- **Retrieval**: find the pieces of text that matter for a question.
- **Augmented**: add those pieces to the prompt.
- **Generation**: the model writes the answer from them.

Almost every "chat with your documents" product is RAG.

## Why do we need it?

Remember lesson 32: a model has gaps. It does not know your private documents. It does not know news after its cutoff date. When it does not know, it may **make things up**.

Three ways to fix it:

| Way | What it does | Problem |
| --- | --- | --- |
| Paste everything in the prompt | The model sees all your docs | Context window is limited. You pay for every token, every call. |
| Fine-tune the model | Changes its dials | Teaches style, not reliable facts. Slow and costly to update. |
| **RAG** | Fetch only the useful pieces, then ask | Needs a good search. |

Think of an **open-book exam**. The student does not memorize the whole book. They look up the right page, read it, and then write the answer. RAG does the same. Your search finds the page. The model reads it and answers.

## The two phases

RAG has two parts that run at different times:

```
Phase 1: INDEXING (offline, once, then when docs change)
   documents -> clean -> chunk -> embed -> store in a vector database

Phase 2: QUERYING (online, for every question)
   question -> embed -> search the store -> top chunks
            -> put chunks + question in a prompt -> model -> answer
```

You built most of phase 1 in Level 3 (chunking, embedding, Chroma). In this lesson you build phase 2: from top chunks to a final answer.

## Step 1: from search to hits

A search gives you a score for each chunk. A **hit** is a chunk together with its score. Keep the best `k`, and drop the ones that are too weak (lesson 15: a minimum score).

Let's practise the pattern with a different example: shop items with a rating. We keep the best `k` items that are good enough.

1. Join each item with its rating, into a new dictionary (do not change the old one).
2. Sort best first. `sorted(..., key=function, reverse=True)` sorts by what the function returns. Python's sort keeps equal items in their old order.
3. Take the first `k`.
4. Drop those below the minimum.

```python
def rating(item):
    return item["rating"]

def best_items(names, ratings, k, minimum):
    items = []
    for name, value in zip(names, ratings):
        items.append({"name": name, "rating": value})
    items = sorted(items, key=rating, reverse=True)
    return [item for item in items[:k] if item["rating"] >= minimum]

best_items(["pen", "ink", "pad"], [3, 5, 4], 2, 4)
# -> [{'name': 'ink', 'rating': 5}, {'name': 'pad', 'rating': 4}]
best_items(["pen", "ink", "pad"], [3, 5, 4], 3, 4.5)
# -> [{'name': 'ink', 'rating': 5}]
```

`zip(names, ratings)` walks two lists together. The same pattern is the first exercise, with chunks and scores.

## Step 2: put the chunks in the prompt

The model reads text, so turn the hits into text. Two rules:

1. **Number them.** `[1]`, `[2]`... In the next lesson the model uses these numbers to cite its sources.
2. **Say where they came from.** A label like `tasks.md > Delete`.

```
[1] tasks.md > Delete
Use the DELETE endpoint to remove a task.

[2] auth.md
Send your token in the Authorization header.
```

The pattern is a numbered list. Let's practise it with another example: a to-do list.

1. Make an empty list `lines`.
2. Loop with `enumerate(items, start=1)` so the counter starts at 1.
3. Add `f"{number}. {item}"` for each.
4. Join the lines with `"\n"`.

```python
def numbered(items):
    lines = []
    for number, item in enumerate(items, start=1):
        lines.append(f"{number}. {item}")
    return "\n".join(lines)

numbered(["wash", "cook"])   # -> '1. wash\n2. cook'
numbered([])                  # -> ''
```

## Step 3: the RAG prompt

A RAG prompt has three parts:

- **Rules** (system message): "Answer only from the context. If the answer is not there, say you do not know."
- **Context**: the numbered chunks.
- **Question**: what the user asked.

```
system: Answer the question using only the context.
        If the answer is not in the context, reply exactly: I don't know.
user:   Context:
        [1] tasks.md > Delete
        Use the DELETE endpoint to remove a task.

        Question: How do I delete a task?
```

The rule "only the context" is what turns a model that *guesses* into a model that *reads*. The "I don't know" rule gives it a safe way out (lesson 7).

Where should the context go? Put it in the **user** message, next to the question. It changes on every call. The system message stays the same, which is good for caching (lesson 2).

## Step 4: "I don't know" before the call

What if the search found nothing good? Then the model has nothing to read. If you call it anyway, it might guess. So check first:

- No hits after the minimum score? Return "I don't know." **without calling the model.** It saves money and avoids a made-up answer.

This two-layer idea matters: **the search decides whether there is an answer; the model only writes it.**

## The whole function

`answer(client, retrieve, question)`:

1. `hits = retrieve(question, k)`, keep the good ones.
2. No hits? Return "I don't know." (no call).
3. Build the messages. Call the model with `temperature=0` (we want facts).
4. Return the text **and** the hits. The hits let you show sources, and they help you debug.

Note that `retrieve` is a **function that you pass in** (lesson 14). A real one embeds the question and searches Chroma. A test one just returns a fixed list. The function `answer` does not care.

## Try it live

Build a real RAG over this project's reference docs:

1. Index `reference/genai-groq.md` and `reference/genai-retrieval.md` with your chain from lesson 17 (chunk, embed with `fastembed`, store in Chroma).
2. Write `retrieve(question, k)` that embeds the question and queries Chroma.
3. Ask 3 questions whose answers are in the files. Print the answer and the sources.
4. Ask one question that is **not** in the files (*"Who won the 2018 World Cup?"*). Does your bot say "I don't know"? Try it with and without a `min_score`.

## A little deeper

- **Context size.** More chunks is not always better. Extra chunks add noise and cost. Start with `k` = 3 to 5.
- **Order.** Models pay more attention to the start and the end of the context (lesson 24).
- **Chunk text vs parent text.** You can search small chunks and send the bigger section around them.
- **Temperature 0** reduces creative drift. For facts, it is the right choice.
- **Add the date.** For time-sensitive answers, put today's date in the prompt.
- **RAG does not remove hallucination.** The model can still misread the context. Citations (next lesson) and checks (lessons 24 and 25) help.
- **Latency.** RAG adds the search time (small) and a longer prompt (more input tokens, so a slower first token).
- **Where the facts come from.** Wrong or old documents give wrong answers. RAG is only as good as its data.

## Common mistakes

- Calling the model even when the search found nothing useful.
- Not telling the model to use only the context.
- No numbers or sources on the chunks, so nothing can be cited.
- Changing the original chunk dictionaries while adding scores (copy them).
- Using a high temperature for factual answers.
- Pasting far too many chunks "to be safe".

## Interview corner

**What is RAG and why use it?**
Retrieval-Augmented Generation: find relevant text first, add it to the prompt, and let the model answer from it. It gives answers from private or fresh data, reduces made-up answers, and cites sources. Updating knowledge means updating documents, not retraining.

**RAG or fine-tuning?**
RAG for facts that change or are private. Fine-tuning for style, format and behaviour. They can be used together.

**What are the two phases of a RAG system?**
Indexing (offline): clean, chunk, embed and store documents. Querying (online): embed the question, search, build the prompt, generate.

**What do you do when retrieval finds nothing relevant?**
Use a minimum score. If no chunk passes, answer "I don't know" without calling the model, or ask the user to rephrase.

## Summary

- RAG = retrieve relevant chunks, add them to the prompt, generate the answer from them.
- Two phases: indexing (offline) and querying (online).
- A hit is a chunk plus its score. Keep the top `k` above a minimum score.
- Number the chunks and label their source. Put them in the user message.
- Tell the model: answer only from the context, otherwise reply "I don't know".
- No good hits means no model call.
- `retrieve` is a function you pass in, so tests can fake it.
- Project: step 12 adds `copilot/rag.py` and `copilot/rag_cli.py`: the RAG pipeline.
- Reference: `reference/genai-retrieval.md`.
