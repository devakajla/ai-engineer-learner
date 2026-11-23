---
title: "RAG beyond the basics: parent-child, contextual chunks, GraphRAG, agentic RAG"
summary: A tour of the advanced RAG ideas you will hear in interviews and meet in real projects, with small code for the three simplest ones.
plan_ids: []
---

This is an **awareness** lesson. You will not build everything here. The goal: know the names, know the problem each idea solves, and know when it is worth the extra work. Three of the ideas have small exercises.

First the rule of the road: **start with the plain pipeline** (lesson 21), measure it (lesson 25), find the failures (lesson 24), and only then add an idea that fixes *that* failure. Each idea below has a cost.

## 1. Contextual chunks

**Problem:** a chunk by itself can be unclear. `"The limit is 100."` does not say which limit. Its vector is vague, and a search for "free plan rate limit" may miss it.

**Idea:** before embedding, add the context the chunk lost: the document title and the heading path.

```
Rate limits > Free plan

The limit is 100.
```

Now the vector knows what the 100 is about. This is cheap and very effective. You save the chunk with this label for the search, and you can still show the plain text to the user.

A stronger version (named **contextual retrieval** by Anthropic) asks a model to write one or two sentences of context for each chunk, using the whole document, and puts them in front of the chunk before embedding (and before BM25 indexing). It costs one model call per chunk at ingestion time, once. Prompt caching (lesson 41) makes it cheaper. Check the current docs for details.

Let's practise the "label plus text" step with a different example: add a sender and a date in front of a chat message, leaving out empty parts.

1. Collect the parts that are not empty.
2. If there are none, return the text unchanged.
3. Otherwise join the parts with `" | "`, then a blank line, then the text.

```python
def label_message(text, sender="", day=""):
    parts = [part for part in (sender, day) if part]
    if not parts:
        return text
    return " | ".join(parts) + "\n\n" + text

label_message("ok, see you", "Asha", "Mon")   # -> 'Asha | Mon\n\nok, see you'
label_message("ok, see you")                    # -> 'ok, see you'
```

`[part for part in (sender, day) if part]` keeps only the non-empty texts (an empty text counts as false). The first exercise is this shape.

## 2. Parent-child retrieval (small to big)

**Problem:** small chunks match precisely, but they are too small to answer from. Big chunks give complete answers, but their vectors are vague.

**Idea:** use both. Cut the documents into **small child chunks** (a few sentences) and keep a link to the bigger **parent** (the whole section). Search the **children**. Then give the model the **parents** of the best children.

```
search over:   child chunks   (precise)
send to model: parent section (complete)
```

Details to handle:
- Many children can share one parent. Send the parent **once**, with the best score of its children.
- Keep the order of the first hit.
- A hit that has no parent stays as it is.
- The parent must fit your context budget. Sometimes you send the child and its neighbours (a window) instead.

Let's practise the "merge by group" shape with a different example: students scored on questions. Group the scores by class and keep the best score of each class, in order of first appearance.

1. Keep a list `order` of classes in the order you first see them.
2. Keep a dictionary `best` with the highest score per class.
3. For a new class, add it to both. For a known class, update the score only if it is higher.
4. Build the result from `order`.

```python
def best_per_class(scores, class_of):
    order = []
    best = {}
    for name, score in scores:
        group = class_of[name]
        if group not in best:
            order.append(group)
            best[group] = score
        elif score > best[group]:
            best[group] = score
    return [(group, best[group]) for group in order]

class_of = {"Ria": "A", "Sam": "B", "Tia": "A"}
best_per_class([("Ria", 5), ("Sam", 7), ("Tia", 9)], class_of)   # -> [('A', 9), ('B', 7)]
```

The second exercise uses the same pattern, with hits and parents.

## 3. Multi-hop questions and query decomposition

**Problem:** "Which plan has the higher rate limit, Free or Pro?" needs **two** facts from two places. One search with one query often finds only one of them.

**Idea:** **decompose** the question into sub-questions ("rate limit of Free", "rate limit of Pro"), search for each (lesson 23: multi-query is a cousin), collect the evidence, and then answer. It is the first step towards agents.

## 4. Agentic RAG

In plain RAG the code decides everything: always one search, always `k` chunks, then answer. In **agentic RAG** the **model decides** what to do, using tools (lesson 11):

- Which source to search (the API docs, the HR policy, the web)?
- Is the evidence enough, or should I search again with a different query?
- Should I break the question into parts?
- Is the answer supported, or should I say "I don't know"?

```
question -> [model: plan] -> search tool -> [model: enough?] -> (search again) -> answer
```

Benefits: handles multi-hop and vague questions, can use several sources, can fix a bad first search. Costs: more model calls (slower, more expensive), less predictable, harder to test, can loop forever. So you add a **step limit** and a cost cap (Level 5 covers agents in depth).

The smallest agentic step is **routing**: let a model pick the right source for the question. You write one in the third exercise. Always check the model's choice against your list of valid sources.

Let's practise the "ask, clean, check against the list" shape with a different example: ask a model which room a guest should go to.

1. Build the instruction from the allowed names.
2. Call the model.
3. Clean the reply (`strip`, `lower`, remove a final dot).
4. Return it only if it is in the allowed list. Otherwise return `None`.

```python
def choose_room(client, guest, rooms):
    names = ", ".join(rooms)
    system = "Pick the best room for the guest. Reply with only one of: " + names + ", or none."
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": guest}],
        temperature=0,
    )
    name = response.choices[0].message.content.strip().lower().strip(".")
    if name in rooms:
        return name
    return None
```

If the model replies `"Garden."`, you get `"garden"` (when it is in `rooms`). If it makes up `"roof"`, you get `None`. The model's text is never trusted without the check.

## 5. GraphRAG

**Problem:** some questions are about **relations** or the **whole corpus**: "Which teams depend on the billing service?", "What are the main themes across all incident reports?" Chunks of text, found by similarity, are poor at this.

**Idea:** build a **knowledge graph** at ingestion time. A model extracts **entities** (things: services, people, products) and **relations** between them ("checkout *depends on* billing"). Store them as nodes and edges. At question time:

- Follow the edges from the entities in the question (graph traversal) to collect connected facts.
- Or, in Microsoft's GraphRAG style: group the graph into **communities**, write a summary of each community, and answer broad questions from those summaries.

Costs: a lot of model calls at ingestion (expensive), more moving parts (a graph store), and extraction mistakes become permanent. It pays off when your data is rich in relations and your questions are multi-hop or about "everything". For most FAQ and docs bots, hybrid search plus a reranker is enough.

## 6. A short list of other ideas

| Idea | One-line meaning |
| --- | --- |
| **HyDE** (lesson 23) | Search with a model-written fake answer instead of the question |
| **Late interaction (ColBERT)** | Many small vectors per text (one per token), compared in detail. More accurate, more storage |
| **RAPTOR** | Build a tree of summaries (chunks, summaries of chunks, summaries of summaries) and search at all levels |
| **Sentence-window retrieval** | Search single sentences, send the sentence and the ones around it |
| **Self-RAG / CRAG** | The model grades the retrieved chunks and decides to answer, search again or search the web |
| **Fine-tuned embeddings** | Train the embedding model on your own question and chunk pairs to improve recall |
| **Structured and SQL retrieval** | For tables and numbers, let the model write a query (carefully limited) instead of searching text |

## How to choose

| You see this failure | Try this first |
| --- | --- |
| Chunks are vague without context | Contextual chunks |
| Right chunk found but too small to answer | Parent-child, or a sentence window |
| Exact names and codes missed | Hybrid search (lesson 18) |
| Right chunk at rank 8 | Reranker (lesson 23) |
| Follow-up questions fail | Query rewriting (lesson 23) |
| Question needs several facts | Decomposition, agentic RAG |
| Questions about relations or the whole corpus | GraphRAG |
| Several sources | Routing, agentic RAG |

Measure each change on the golden set (lessons 25 and 41). If a fancy idea does not move the numbers, drop it.

## Try it live

1. Take 10 chunks from your docs. Add title and heading labels (`contextualize`). Embed both the plain and the labelled versions. For 5 questions, compare which version ranks the right chunk higher.
2. Cut one document into child chunks of 2 sentences, and keep the parent section. Search the children, and show the parent. Compare the answers with plain chunk retrieval.
3. Write a router with two sources (two Chroma collections) and ask 5 questions. How often does the model pick the right source? Add a question that fits none.
4. Pick one multi-hop question. Try it with plain RAG, then split it in two sub-questions by hand and merge the evidence. Did the answer improve?

## A little deeper

- **Cost of context.** The contextual chunk text is embedded, so it adds a few tokens to every chunk. That is small. The model-written context costs more, but you pay it once at ingestion.
- **Parent size.** Parents that are too big bring back the "noise" problem and "lost in the middle" (lesson 24). 500 to 2000 tokens is common. Measure.
- **Agent loops need brakes.** Max steps, max tokens, a time limit, and logging of each step (Level 5).
- **Graph quality.** Extraction by a model can miss or invent relations. Check a sample by hand, and keep the source chunk id for every edge, so you can show proof.
- **Not either/or.** A strong system often combines: contextual chunks, hybrid search, a reranker, parent expansion, and a router.
- **Hype check.** New RAG names appear every month. Ask: what failure does it fix, what does it cost, and how do I measure it?

## Common mistakes

- Adding advanced RAG before measuring the plain version.
- Parent-child with parents that are too big for the context budget.
- Sending the same parent several times.
- Letting an agent search forever with no step limit.
- Using GraphRAG for a small FAQ bot.
- Trusting the router's reply without checking it against the valid sources.

## Interview corner

**What is parent-child (small-to-big) retrieval?**
Search small child chunks for precision, then send the larger parent sections to the model for complete context. Merge children that share a parent.

**What is contextual retrieval?**
Add context (title, heading, or a model-written summary of where the chunk sits in the document) to each chunk before embedding and BM25 indexing, so chunks that are unclear alone become findable.

**What is agentic RAG, and what are its risks?**
The model decides how to search: which source, whether to search again, whether to split the question. It handles harder questions, but it is slower, costs more, is less predictable, and can loop, so it needs step limits, cost caps and logging.

**When would you use GraphRAG?**
When the data is full of relations or the questions are multi-hop or about the whole corpus. It costs a lot to build (entity extraction), so for plain document Q&A use hybrid search and a reranker first.

**A user asks something that needs two documents. How do you handle it?**
Decompose the question into sub-questions, retrieve for each, merge and deduplicate the evidence (for example with RRF), and answer with citations. Or let an agent do the steps with a limit.

## Summary

- Start with plain RAG, measure it, and add an idea only when it fixes a measured failure.
- Contextual chunks: add title and heading (or a model-written context) before embedding.
- Parent-child: search small chunks, send the bigger parent section once, with the best child score.
- Multi-hop questions: decompose into sub-questions.
- Agentic RAG: the model chooses sources and steps. It needs step limits and checks.
- Routing: always check the model's choice against the valid sources.
- GraphRAG: a knowledge graph of entities and relations, good for relations and whole-corpus questions, expensive to build.
- Others to know by name: HyDE, ColBERT, RAPTOR, sentence-window, Self-RAG/CRAG, fine-tuned embeddings, SQL retrieval.
- Reference: `reference/genai-retrieval.md`.
